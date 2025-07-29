import html
import logging
import re
from functools import cached_property
from typing import Any

import gruel
from bs4 import BeautifulSoup, Tag
from pathier import Pathier

import rebay.models as models

root = Pathier(__file__).parent


class EbayParser:
    """Base class for ebay parsers."""

    def __init__(self, page_source: str, url: gruel.Url, logger: logging.Logger):
        self.source = page_source
        self.url = url
        self.soup = BeautifulSoup(self.source, "html.parser")
        self.body = self.soup.find("body")
        self.logger = logger
        self.mappings = models.Mappings.load()


class ShopPageParser(EbayParser):
    """Ebay shop page parser."""

    @property
    def listings_per_page(self) -> int:
        return 240

    @cached_property
    def num_pages(self) -> int:
        pagination = self.soup.find("ol", class_="pagination__items")
        if isinstance(pagination, Tag):
            last_page = pagination.find_all("li", recursive=False)[-1]
            assert isinstance(last_page, Tag)
            return int(last_page.text)
        return 1

    @cached_property
    def listings(self) -> list[Tag]:
        assert isinstance(self.body, Tag)
        return self.body.select(".srp-main div .srp-river-main ul .s-item")  # type: ignore

    @cached_property
    def listing_urls(self) -> list[gruel.Url]:
        assert isinstance(self.body, Tag)
        raw_urls = [
            listing.select(".s-item__info a", limit=1)[0].get("href")  # type: ignore
            for listing in self.listings
        ]
        urls: list[gruel.Url] = []
        for url in raw_urls:
            assert isinstance(url, str)
            url = gruel.Url(url)
            url.query = ""
            urls.append(url)
        return urls

    @cached_property
    def is_valid(self) -> bool:
        """Returns `True` if the search page resolved to the intended category.

        Returns `False` if the category was invalid and the page reverts to displaying entire shop.
        """
        assert isinstance(self.body, Tag)
        scope_li = self.body.find("li", class_="srp-refine__category__item")
        if not isinstance(scope_li, Tag):
            return True
        child = list(scope_li.children)[0]
        if isinstance(child, Tag):
            return child.name == "a"
        return False


class ListingParser(EbayParser):
    """Ebay listing parser.

    `cached_properties` are generally raw parsed items from the given page source.

    `get_{thing}()` functions are generally for converting the raw item to the Reverb compatible version.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    @cached_property
    def title(self) -> str:
        head = self.soup.find("head")
        assert isinstance(head, Tag)
        title = head.find("title")
        assert isinstance(title, Tag)
        title = title.text
        title = title[: title.rfind("|")].strip()
        return html.unescape(title)

    @cached_property
    def condition(self) -> str:
        assert isinstance(self.body, Tag)
        return (
            self.body.select(".ux-icon-text__text", limit=1)[0]  # type: ignore
            .select(".ux-textspans")[0]
            .text
        )

    @cached_property
    def inventory(self) -> int | str:
        assert isinstance(self.body, Tag)
        # Not sure if `.d-quantity__availability` is still in use
        quantity = self.body.select(".d-quantity__availability", limit=1)  # type: ignore
        self.logger.debug(f".d-quantity__availability tag for {self.url}: {quantity}")
        if not quantity:
            quantity = self.body.findAll("div", class_="x-quantity__availability")
        self.logger.debug(f"x-quantity__availability tag for {self.url}: {quantity}")
        if not quantity:
            self.logger.info(
                f"No explicit quantity found for {self.url}. Defaulting to 1."
            )
            return 1
        text = quantity[0].text
        self.logger.debug(f"Quantity tag text: {text}")
        if "Out of Stock" in text:
            self.logger.warning(f"Out of stock for listing {self.url} .")
            return text
        if "available" in text:
            try:
                return int(text.split()[0])
            except Exception as e:
                self.logger.warning(f"Unspecified quantity for listing {self.url} .")
                return text
        if "last one" in text.lower():
            return 1
        return int(text)

    @cached_property
    def item_specifics_columns(self) -> list[Tag]:
        assert isinstance(self.body, Tag)
        try:
            tabs_cell = self.body.select(".tabs__content", limit=1)[0]  # type: ignore
            return tabs_cell.select(".ux-layout-section-evo__col")  # type: ignore
        except Exception as e:
            self.logger.warning(
                f"Could not find item specifics section for listing {self.url} ."
            )
            return []

    def get_from_item_sepecifics_columns(self, category: str) -> str:
        """Returns the value for `category` in the page's "Item specifics" section.

        Returns an empty string if it couldn't be found."""
        for col in self.item_specifics_columns:
            content = col.find_all("span", class_="ux-textspans")
            if len(content) == 2:
                label = content[0].text
                value = content[1].text
                if label.strip() == category:
                    return value.strip()
        return ""

    @cached_property
    def make(self) -> str:
        return self.get_from_item_sepecifics_columns("Brand")

    @cached_property
    def model(self) -> str:
        return self.get_from_item_sepecifics_columns("Model")

    @cached_property
    def year(self) -> str:
        return self.get_from_item_sepecifics_columns("Model Year")

    @cached_property
    def finish(self) -> str:
        return self.get_from_item_sepecifics_columns("Body Color")

    def is_valid_price(self, price: str) -> bool:
        price = price.replace(",", "").replace(".", "")
        return price.isnumeric()

    @cached_property
    def price(self) -> str:
        assert isinstance(self.body, Tag)
        text = self.body.select(".x-price-primary", limit=1)[0].text.replace("$", "")  # type: ignore
        texts = text.split()
        num_chunks = len(texts)
        if num_chunks < 2:
            self.logger.warning(
                f"Price error: could not find price text for {self.url} : found `{text}`"
            )
            return "N/A"
        if num_chunks > 2:
            self.logger.warning(
                f"Price error: price may have been incorrectly parsed for {self.url} : text does not match format: `<currency> <price>`: found `{text}`"
            )
            return texts[1]
        price = texts[1]
        if not self.is_valid_price(price):
            self.logger.error(
                f"Price error: price value for {self.url} is not a valid number: found `{text}` : `{price}`"
            )
        return price

    @cached_property
    def breadcrumbs(self) -> list[Tag]:
        assert isinstance(self.body, Tag)
        return self.body.select(".seo-breadcrumb-text span")  # type: ignore

    @cached_property
    def product_type(self) -> str:
        crumbs = self.breadcrumbs
        if "See more" in crumbs[-1].text:
            return crumbs[-2].text
        return crumbs[-1].text

    def _get_image_urls_regex(self) -> list[str]:
        # Narrow down page source
        pic_panel = self.soup.find("div", attrs={"id": "PicturePanel"})
        pattern = (
            r"https://i.ebayimg.com/images/[\w]+/[-a-zA-Z0-9~]+/s-l[0-9]+.[\w]{3,4}"
        )
        image_urls = re.findall(pattern, str(pic_panel))
        strained_image_urls: list[str] = []
        for url in image_urls:
            url = url[: url.rindex("l") + 1] + "2000.jpg"
            if url not in strained_image_urls:
                strained_image_urls.append(url)
        return strained_image_urls

    @cached_property
    def image_urls(self) -> list[str]:
        assert isinstance(self.body, Tag)
        images = [
            str(image.get("src"))
            for image in self.body.select("div .ux-image-filmstrip-carousel img")  # type: ignore
        ]
        # If images is empty, that seems to indicate the listing has only one image and needs to be addressed by a different path.
        if not images:
            try:
                image_tag = self.body.find(
                    "img", class_="ux-image-magnify__image--original"
                )
                assert isinstance(image_tag, Tag)
                return [str(image_tag.get("src"))]
            except Exception as e:
                self.logger.error("Image")
                image_tag = self.body.find("img", class_="img-scale-down")
                assert isinstance(image_tag, Tag)
                return [str(image_tag.get("src"))]
        return images

    def get_condition(self) -> str:
        """Get the mapped item condition."""
        return self.mappings.item_conditions.get(self.condition, self.condition)

    def get_inventory(self) -> int | str:
        """Get inventory count."""
        try:
            inventory = self.inventory
        except Exception as e:
            self.logger.exception(
                f"Error parsing inventory for {self.url} - defaulting to 1"
            )
            inventory = 1
        return inventory

    def get_make(self) -> str:
        if not self.make:
            self.logger.debug(
                f"No make found for {self.url} in {self.item_specifics_columns}."
            )
        return self.make

    def get_model(self) -> str:
        if not self.model:
            self.logger.debug(
                f"No model found for {self.url} in {self.item_specifics_columns}."
            )
            return "Please add model."
        return self.model

    def get_year(self) -> str:
        if not self.year:
            self.logger.debug(
                f"No year found for {self.url} in {self.item_specifics_columns}."
            )
        return self.year

    def get_finish(self) -> str:
        if not self.finish:
            self.logger.debug(
                f"No finish found for {self.url} in {self.item_specifics_columns}."
            )
        return self.finish

    def get_product_type(self) -> str:
        """Go through `breadcrumbs` to find product_type and return the mapped version.

        Returns an empty string if not found."""
        for crumb in self.breadcrumbs[::-1]:
            text = crumb.text
            for reverb_category, ebay_category in self.mappings.product_types.items():
                if text in ebay_category:
                    return reverb_category
        crumbs = ":".join(crumb.text for crumb in self.breadcrumbs)
        self.logger.warning(
            f"No breadcrumbs for listing {self.url} were found in product type mappings.\nBreadcrumbs: {crumbs}"
        )
        return ""

    def get_images(self, image_limit: int = 25) -> list[str]:
        """Return a list of image urls with higher resolution stems."""
        # Image urls are in the format:
        # https://i.ebayimg.com/images/g/{id_string}/s-l{number}.jpg
        images = self._get_image_urls_regex()[:image_limit]
        self.logger.debug(f"Found {len(images)} images for {self.url}.")
        if not images:
            raise RuntimeError(f"No images found for listing {self.url}.")
        return images


class DescriptionParser(EbayParser):
    """Description page parser."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.logger.debug(f"Body content for description page:\n{self.body}")

    @cached_property
    def description(self) -> str:
        assert isinstance(self.body, Tag)
        lines = [line for line in self.body.text.splitlines()]
        # Remove "empty" lines from the beginning of the description
        i = 0
        for i, line in enumerate(lines):
            if len(line.split()):
                break
        lines = lines[i:]
        return "\n".join(lines)

    @cached_property
    def html_no_scripts(self) -> str:
        """Returns the source HTML without any `script` tags."""
        soup = self.soup
        for script in soup.find_all("script"):
            script.extract()
        content = str(soup)
        # remove the _gsrx div if it exists
        # remove ebay title tag
        content = content.replace("_gsrx_vers_1547 (GS 9.4.2 (1547))", "").replace(
            "<title>eBay</title>", ""
        )
        self.logger.debug(f"No script description content for {self.url}:\n{content}")
        # Google Drive has a max character per cell limit
        max_characters = 50000
        content_length = len(content)
        if content_length > max_characters:
            self.logger.warning(
                f"Description HTML for listing {self.url} exceeds Drive's character limit of 50k (content is `{content_length}`). Falling back on text only."
            )
            content = self.description
        return content
