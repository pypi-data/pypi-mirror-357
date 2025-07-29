import argparse

import gruel

from rebay.engine import RebayEngine


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "shop_name", type=str, help=""" The name of the shop to scrape. """
    )

    parser.add_argument("listing_url")
    parser.add_argument(
        "-s", "--save", action="store_true", help=""" Save result to csv."""
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help=""" Run with logging level 'DEBUG'. """,
    )
    args = parser.parse_args()

    return args


def main(args: argparse.Namespace | None = None):
    if not args:
        args = get_args()
    args.listing_url = gruel.Url(args.listing_url)
    engine = RebayEngine(args.shop_name, 5)
    if args.debug:
        engine.logger.setLevel("DEBUG")
    engine.prescrape_chores()
    listing = engine.parse_item(args.listing_url)
    assert listing
    print(listing)
    engine.shop.listings.append(listing)
    if args.save:
        stem = engine.shop.output_path.stem
        save_path = engine.shop.output_path.with_stem(f"{stem}_single")
        engine.shop.save_to_csv(save_path)
        save_path.write_text(
            save_path.read_text(encoding="utf-8").replace('""', '"'), encoding="utf-8"
        )


if __name__ == "__main__":
    main(get_args())
