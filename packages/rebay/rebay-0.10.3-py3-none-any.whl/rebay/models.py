import csv
import itertools
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from functools import cached_property

import dacite
import gruel
import loggi
from pathier import Pathier, Pathish
from typing_extensions import Self

root = Pathier(__file__).parent


@dataclass
class Listing:
    url: gruel.Url
    new_listing: str = "TRUE"
    title: str = ""
    condition: str = ""
    inventory: int | str = 1
    sku: int | str = ""
    make: str = ""
    model: str = ""
    year: str = ""
    finish: str = ""
    price: str = ""
    product_type: str = ""
    image_urls: list[str] = field(default_factory=list[str])
    shipping_price: str = "0"
    upc_does_not_apply: str = "TRUE"
    description: str = ""

    def __str__(self) -> str:
        return "\n".join(
            f"{key}: {value}"
            for key, value in {  # type: ignore
                "title": self.title,
                "url": str(self.url),
                "condition": self.condition,
                "inventory": self.inventory,
                "sku": self.sku,
                "make": self.make,
                "model": self.model,
                "year": self.year,
                "finish": self.finish,
                "price": self.price,
                "product_type": self.product_type,
                "images": "\n".join(self.image_urls),
            }.items()
        )


@dataclass
class Shop:
    name: str
    listings: list[Listing] = field(default_factory=list[Listing])
    start: datetime = datetime.now()
    domain: str = "com"

    def __post_init__(self):
        self.start = datetime.now()

    @cached_property
    def logpath(self) -> Pathier:
        return Pathier(f"logs/{self.name}.log")

    @cached_property
    def url(self) -> gruel.Url:
        return gruel.Url(f"https://www.ebay.{self.domain}/usr/{self.name}")

    @property
    def output_path(self) -> Pathier:
        return Pathier.cwd() / "rebay_output" / self.name / f"{self.name}_data.csv"

    def get_rejected_listings(self) -> list[str]:
        """Get log messages for listings that were rejected."""
        log = (
            loggi.load_log(self.logpath)
            .filter_dates(self.start)
            .filter_messages(["Tossing out*"])
        )
        return [event.message for event in log.events]

    def get_inventory_warning_item_numbers(self) -> list[int]:
        """Get the item numbers of listings that didn't have a concrete quantity."""
        log = (
            loggi.load_log(self.logpath)
            .filter_dates(self.start)
            .filter_levels(["WARNING"])
            .filter_messages(["Unspecified quantity*", "Out of stock*"])
        )
        return self.get_item_numbers_from_events(log.events)

    def get_errored_listing_item_numbers(self) -> list[int]:
        """Get the item numbers of listings that had parse errors."""
        log = (
            loggi.load_log(self.logpath)
            .filter_dates(self.start)
            .filter_levels(["ERROR", "WARNING"])
            .filter_messages([f"*https://www.ebay.{self.domain}/itm/*"])
        )
        return self.get_item_numbers_from_events(log.events)

    def get_description_warning_item_numbers(self) -> list[int]:
        """Get the item numbers of listings with description length warnings."""
        log = (
            loggi.load_log(self.logpath)
            .filter_dates(self.start)
            .filter_levels(["WARNING"])
            .filter_messages(["Description HTML for listing*"])
        )
        return self.get_item_numbers_from_events(log.events)

    def get_item_numbers_from_events(self, events: list[loggi.Event]) -> list[int]:
        item_numbers: list[int] = []
        for event in events:
            hits = re.findall(r"(https[a-zA-Z0-9\.\:/]+) ", event.message)
            if hits:
                item_number = hits[0]
                if item_number not in item_numbers:
                    item_numbers.append(int(item_number[item_number.rfind("/") + 1 :]))
        return item_numbers

    def get_csv_indicies(self, item_numbers: list[int]) -> list[int]:
        """Get the indicies (1-indexed) of listings for `item_numbers`."""
        indicies: list[int] = []
        for i, listing in enumerate(self.listings):
            if listing.sku in item_numbers:
                # Adding 2 b/c headers will show up as row 1
                indicies.append(i + 2)
        return indicies

    def get_page_url(self, page_num: int = 1, category_num: int = 619) -> gruel.Url:
        """Returns this shop's url for the specified page number.

        `category_num` defaults to "Musical Instruments & Gear"."""
        return gruel.Url(
            f"https://www.ebay.{self.domain}/sch/i.html?_from=R40&_nkw=&_sacat={category_num}&LH_TitleDesc=0&_sasl={self.name}&_fss=1&LH_SpecificSeller=1&_saslop=1&_ipg=240&_sop=10&_pgn={page_num}"
        )

    def _convert_image_urls(self, listing: dict[str, str]) -> dict[str, str]:
        max_images = 25
        image_keys = [f"product_image_{i}" for i in range(1, max_images + 1)]
        urls = listing.pop("image_urls")[:max_images]
        for image_key, url in itertools.zip_longest(image_keys, urls, fillvalue=""):
            listing[image_key] = url
        return listing

    def save_to_csv(self, path: Pathish | None = None):
        """Save this shop to a `.csv` file at the path `{current_working_directory}/output/{shop_name}/{shop_name}_data.csv` if `path` isn't given."""
        if not path:
            path = self.output_path
        else:
            path = Pathier(path)
        path.parent.mkdir()
        with path.open("w", newline="", encoding="utf-8") as file:
            rows = [asdict(listing) for listing in self.listings]
            # Convert image url list to appropriate keys
            # And remove url
            for row in rows:
                row.pop("url")
                row = self._convert_image_urls(row)
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def get_no_description_listings(self) -> list[int]:
        """Return csv indicies for listings that have empty descriptions."""
        return [
            i for i, listing in enumerate(self.listings, 2) if not listing.description
        ]

    def get_csv_row_url_map(self) -> dict[int, gruel.Url]:
        """Return a dict where keys are csv rows and values are listing urls."""
        return {i: listing.url for i, listing in enumerate(self.listings, 2)}

    def save_csv_row_url_map(self, map_: dict[int, gruel.Url] | None = None):
        """Save the map. If one isn't given, call `get_csv_row_url_map()`."""
        if not map_:
            map_ = self.get_csv_row_url_map()
        self.output_path.with_name("csv_row_url_map.json").dumps(
            map_, indent=2, default=str, encoding="utf-8"
        )


@dataclass
class Mappings:
    product_types: dict[str, list[str]]
    item_conditions: dict[str, str]
    category_page_numbers: dict[str, int]

    @classmethod
    def load(cls) -> Self:
        """Return a `Mapping` object populated by `mappings.json`."""
        return dacite.from_dict(cls, (root / "mappings.json").loads())

    def get_category_name(self, category_num: int) -> str:
        """Get the category name from the category number."""
        for category, num in self.category_page_numbers.items():
            if category_num == num:
                return category
        raise ValueError(
            f"{category_num} does not exist in mappings.category_page_numbers."
        )
