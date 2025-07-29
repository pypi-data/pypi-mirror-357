import argparse
import time
from datetime import datetime

import gruel
import loggi
import quickpool
from pathier import Pathier
from printbuddies import ColorMap
from rich import print
from typing_extensions import Any, Sequence, override

import rebay.models as models
import rebay.parsers as parsers
import rebay.utilities as utilities
from rebay.browser import Browser
from rebay.listing_globber import ListingGlobber

root = Pathier(__file__).parent
c = ColorMap()


class RebayEngine(gruel.Gruel):
    def __init__(
        self,
        shop_name: str,
        max_threads: int | None = None,
        description_text_only: bool = False,
        domain: str = "com",
        listing_limit: int | None = None,
    ):
        self.shop = models.Shop(shop_name, domain=domain)
        super().__init__(self.shop.name)
        self.max_threads = max_threads
        self.base_description_url = "https://vi.vipr.ebaydesc.com/itmdesc"
        self.mappings = models.Mappings.load()
        self.description_text_only = description_text_only
        self.listing_limit = listing_limit

    @override
    def get_source(self) -> list[gruel.Url]:
        # Return a list of urls for all the relevant shop listings.
        globber = ListingGlobber(self.shop, self.logger, self.max_threads)
        print(f"{c.p1}Searching {c.cobl}{self.shop.name}[/] for listings.")
        listing_urls = globber.get_all_listing_urls()
        message = f"{c.p1}Found {c.co1}{len(listing_urls)}[/] listings."
        print(message)
        self.logger.info(message)
        return listing_urls[: self.listing_limit]

    @override
    def request(self, *args: Any, **kwargs: Any) -> gruel.Response:
        kwargs["randomize_useragent"] = True
        return super().request(*args, **kwargs)

    def render(self, url: gruel.Url) -> gruel.Response | None:
        """
        Use selenium engine to request the page.

        Args:
            url (gruel.Url): The url to request.

        Returns:
            gruel.Response | None: If the request failed, `None` is returned.
        """
        return Browser.get(url.address, self.logger)

    @override
    def get_parsable_items(self, source: list[gruel.Url]) -> list[gruel.Url]:
        return source

    def get_listing_parser(self, url: gruel.Url) -> parsers.ListingParser | None:
        response = self.render(url)
        if not response:
            self.logger.error(f"Failed to get `ListingParser` for '{url}'.")
            return None
        if response.status_code != 200:
            self.logger.warning(f"{url} returned status code {response.status_code}.")
        parser = parsers.ListingParser(response.text, url, self.logger)
        if self.logger.level == loggi.DEBUG:
            (
                Pathier.cwd()
                / "page_dumps"
                / self.shop.name
                / f"{url.address.replace(':','_').replace('/','_').replace('.','_')}.html"
            ).write_text(parser.source, encoding="utf-8")
        return parser

    def dump_page(self, item_number: str, source: str) -> None:
        (
            self.shop.output_path.parent / "errored_pages" / f"{item_number}.html"
        ).write_text(source)

    def parse_item(self, item: gruel.Url) -> models.Listing | None:
        """Parse the listing located at `item`(url)."""
        item.netloc = item.netloc.replace(self.shop.domain, "com")
        url = item
        try:
            item_number = url.path.split("/")[-1]
            listing = models.Listing(url)
            listing.sku = int(item_number)
            self.logger.debug(f"Getting listing {url}")
            parser = self.get_listing_parser(url)
            if not parser:
                return None
            # If no title, re-request the page
            max_attempts = 5
            attempt = 1
            while attempt <= max_attempts:
                try:
                    self.logger.debug(f"Getting title {url}. (attempt `{attempt}`)")
                    if not parser:
                        return None
                    listing.title = parser.title
                    break
                except Exception as e:
                    self.logger.debug(f"Getting title failed, trying again {url}")
                    time.sleep(1)
                    attempt += 1
                    parser = self.get_listing_parser(url)
            # Sometimes a tv or vcr related thing gets caught up
            terms = [" tv,", " vcr,", " vhs,"]
            toss_terms: list[str] = []
            for term in terms:
                toss_terms.append(term.replace(",", " "))
                toss_terms.append(term)
            self.logger.debug(f"Checking toss list. {url}")
            if any(term in listing.title.lower() for term in toss_terms):
                self.logger.info(
                    f"Tossing out listing with title '{listing.title}'. ({url})"
                )
                return None
            if not parser:
                return listing
            listing.condition = parser.get_condition()
            listing.inventory = parser.get_inventory()
            listing.make = parser.get_make()
            listing.model = parser.get_model()
            listing.year = parser.get_year()
            listing.finish = parser.get_finish()
            listing.price = parser.price
            # Sometimes breadcrumbs don't render on the initial request so try again
            if not parser.breadcrumbs:
                parser = self.get_listing_parser(url)
            if not parser:
                return listing
            listing.product_type = parser.get_product_type()
            try:
                listing.image_urls = parser.get_images()
            except Exception as e:
                parser = self.get_listing_parser(url)
            if not parser:
                return listing
            listing.image_urls = parser.get_images()
            description_url = f"{self.base_description_url}/{item_number}"
            self.logger.debug(f"Using description url: `{description_url}`.")
            description_response = utilities.get_page(description_url)
            self.logger.debug(
                f"Description url return `{description_response.status_code}`."
            )
            parser = parsers.DescriptionParser(
                description_response.text,
                url,
                self.logger,
            )
            if self.description_text_only:
                listing.description = parser.description
            else:
                listing.description = parser.html_no_scripts
            del parser
            self.success_count += 1
            return listing
        except Exception as e:
            self.logger.critical(f"Failure to parse {url}\n" + str(e))
            self.logger.exception("Exception for ^")
            self.fail_count += 1

    @override
    def parse_items(self, parsable_items: Sequence[gruel.Url]) -> list[None]:
        """Multithread parsing `listings`."""
        print(f"{c.p1}Parsing {c.co1}{len(parsable_items)}[/] listings.")
        pool = quickpool.ThreadPool(
            [self.parse_item] * len(parsable_items),
            [(listing,) for listing in parsable_items],
            max_workers=1,  # self.max_threads,
        )
        self.shop.listings = [result for result in pool.execute() if result]
        return []

    @override
    def store_items(self, items: Any) -> None:
        """Store `items`."""
        pass

    def postscrape_chores(self):
        super().postscrape_chores()
        if log_stats := self.get_log_stats():
            print(log_stats)
        if self.shop.listings:
            # ======================================================
            # Save files
            # ======================================================
            self.shop.save_to_csv()
            print(f"{c.p1}Output is located at {c.sg1}{self.shop.output_path}")
            print()
            self.shop.save_csv_row_url_map()
            csv_row_url_map = self.shop.get_csv_row_url_map()
            index_justification = len(str(list(csv_row_url_map.keys())[-1])) + 1

            # ======================================================
            # Check and print warnings/errors
            # ======================================================
            if tossed_out_listings := self.shop.get_rejected_listings():
                print(f"{c.p1}The following listings were tossed out:")
                print(*[tossed_out_listings], sep="\n")
                print()

            def display(item_numbers: list[int]):
                print(
                    *[
                        f"{str(index).ljust(index_justification)}{csv_row_url_map[index]}"
                        for index in self.shop.get_csv_indicies(item_numbers)
                    ],
                    sep="\n",
                )
                print()

            # ------------------------------------------------------
            if rows_to_look_at := self.shop.get_errored_listing_item_numbers():
                print(
                    f"{c.p1}The following rows in {c.sg1}{self.shop.output_path.name}[/] should be checked for accuracy:"
                )
                display(rows_to_look_at)
            # ------------------------------------------------------
            if undefined_quantities := self.shop.get_inventory_warning_item_numbers():
                print(
                    f"{c.p1}The following rows in {c.sg1}{self.shop.output_path.name}[/] have an undefined quantity:"
                )
                display(undefined_quantities)
            # ------------------------------------------------------
            if no_descriptions := self.shop.get_no_description_listings():
                print(f"{c.p1}No descriptions found for csv rows:")
                display(no_descriptions)
            # ------------------------------------------------------
            if description_errors := self.shop.get_description_warning_item_numbers():
                print(
                    f"{c.p1}The following rows had descriptions exceeding the character limit:"
                )
                display(description_errors)
        else:
            print(f"{c.p1}Could not scrape any listings for {c.cobl}{self.shop.name}.")
            print(f"{c.p1}Either they have none or there was an error.")
            print(f"{c.p1}Check {c.sg1}{self.shop.logpath}[/] for details.")

    def get_log_stats(self) -> str | None:
        """Returns a string with the number of oopsies that were logged."""
        log = loggi.load_log(self.shop.logpath)
        log = log.filter_dates(datetime.fromtimestamp(self.timer.start_time - 1))
        errors = len(log.filter_levels(["ERROR"]))
        criticals = len(log.filter_levels(["CRITICAL"]))
        if errors or criticals:
            return f"{c.p1}There were {c.r}{errors}[/] errors and {c.br}{criticals}[/] critical errors.\nSee {c.sg1}{Pathier.cwd()/self.shop.logpath}[/] for details."

    @override
    def _parse_source(self, source: Any):
        """
        Run the parsing workflow and handle errors.
        """
        try:
            self.parsable_items = self.get_parsable_items(source)
            self.logger.info(
                f"{self.name}:get_parsable_items() returned {len(self.parsable_items)} items."
            )
        except Exception:
            self.failed_to_get_parsable_items = True
            self.logger.exception(f"Error in {self.name}:get_parsable_items().")
        else:
            self.parsed_items = self.parse_items(self.parsable_items)
            message = f"{c.p1}Scrape completed in {c.sg1}{self.timer.elapsed_str}[/] with {c.bg}{self.success_count}[/] successes and {c.br}{self.fail_count}[/] failures."
            self.logger.info(
                f"Scrape completed in {self.timer.elapsed_str} with {self.success_count} successes and {self.fail_count} failures."
            )
            print(message)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "shop_name", type=str, help=""" The name of the shop to scrape. """
    )

    parser.add_argument(
        "-dto",
        "--description_text_only",
        action="store_true",
        help=""" For the user description page, only scrape the page text. 
        The default is to scrape the page HTML minus `script` tags.""",
    )

    parser.add_argument(
        "-t",
        "--max_threads",
        type=int,
        default=3,
        help=""" Max number of threads to use. Default is 3. Too many and they'll error page you. """,
    )

    parser.add_argument(
        "-c",
        "--country",
        type=str,
        default="com",
        help=""" The country url domain to use if not "com". (i.e. `-c de` for `ebay.de`) """,
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help=""" Run with logging level 'DEBUG'. """,
    )

    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help=""" Limit the scrape to this many listings.""",
    )
    args = parser.parse_args()
    args.country = args.country.strip(".")

    return args


def main(args: argparse.Namespace | None = None):
    if not args:
        args = get_args()
    engine = RebayEngine(
        args.shop_name,
        args.max_threads,
        args.description_text_only,
        args.country,
        args.limit,
    )
    if args.debug:
        engine.logger.setLevel("DEBUG")
    engine.show_parse_items_prog_bar = True
    engine.scrape()


if __name__ == "__main__":
    main(get_args())
