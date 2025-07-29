from typing import Callable

import gruel
import loggi
import quickpool
from printbuddies import ColorMap, Progress

import rebay.models as models
import rebay.parsers as parsers


class ListingGlobber:
    def __init__(
        self,
        shop: models.Shop,
        logger: loggi.logging.Logger,
        max_threads: int | None = 5,
    ):
        self.shop = shop
        self.logger = logger
        self.max_threads = max_threads
        self.mappings = models.Mappings.load()

    def get_shop_page_parser(
        self, page_num: int, category_num: int
    ) -> parsers.ShopPageParser:
        """Make a request to the shop's page for the given `page_num` and `category_num` and return the parsed object."""
        return parsers.ShopPageParser(
            gruel.request(
                self.shop.get_page_url(page_num, category_num).address,
                logger=self.logger,
                randomize_useragent=False,
            ).text,
            self.shop.url,
            self.logger,
        )

    def _log_page_listings(self, num_listings: int, category: str, page: int):
        """Log number of listings found on a page for a given category."""
        self.logger.info(f"Found {num_listings} listings for '{category}' page {page}.")

    def get_listing_urls_from_page_range(
        self, page_range: tuple[int, int], category_num: int
    ) -> list[gruel.Url]:
        """Returns listing urls for listings on pages `page_range[0]` -> `page_range[1]` for the given `category_num`."""
        get_listing_urls: Callable[
            [int], list[gruel.Url]
        ] = lambda page_num: self.get_shop_page_parser(
            page_num, category_num
        ).listing_urls
        num_pages = page_range[1] - page_range[0]
        pool = quickpool.ThreadPool(
            [get_listing_urls] * (num_pages + 1),
            [(page,) for page in range(page_range[0], page_range[1] + 1)],
            max_workers=self.max_threads,
        )
        results = pool.execute(False)
        urls: list[gruel.Url] = []
        category_name = self.mappings.get_category_name(category_num)
        for i, result in enumerate(results, page_range[0]):
            self._log_page_listings(len(result), category_name, i)
            urls.extend(result)
        return urls

    def get_listing_urls_for_category(self, category_num: int) -> list[gruel.Url]:
        """Get shop listings for a given `category_num`."""
        # shop_url = self.shop.get_page_url(1, category_num)
        parser = self.get_shop_page_parser(1, category_num)
        category_name = self.mappings.get_category_name(category_num)
        if not parser.is_valid:
            self.logger.info(
                f"Category `{category_name}`:`{category_num}` is not valid."
            )
            return []
        self.logger.info(f"Found {parser.num_pages} pages for '{category_name}'.")
        if parser.num_pages == 0:
            return []
        self._log_page_listings(len(parser.listing_urls), category_name, 1)
        if parser.num_pages == 1:
            return parser.listing_urls
        # If there is more than one page, get those as well
        urls = parser.listing_urls
        # If only one more page
        if parser.num_pages == 2:
            parser = self.get_shop_page_parser(2, category_num)
            self._log_page_listings(len(parser.listing_urls), category_name, 2)
            return urls + parser.listing_urls
        # > 2 pages
        urls += self.get_listing_urls_from_page_range(
            (2, parser.num_pages), category_num
        )
        return urls

    def get_all_listing_urls(self) -> list[gruel.Url]:
        """Return listing urls for all categories."""
        listing_urls: list[gruel.Url] = []
        num_categories = len(self.mappings.category_page_numbers)
        c = ColorMap()
        with Progress() as progress:
            scan = progress.add_task("", total=num_categories)
            for category, category_num in self.mappings.category_page_numbers.items():
                progress.update(
                    scan,
                    suffix=f"{c.dp1}Scanning category {c.br}`[/]{c.cobl}{category}[/]{c.br}`",
                )
                urls = self.get_listing_urls_for_category(category_num)
                # No duplicates, please
                urls = [url for url in urls if url not in listing_urls]
                listing_urls.extend(urls)
                self.logger.info(f"Found {len(urls)} unique urls in '{category}'.")
                progress.update(scan, advance=1)
        return listing_urls
