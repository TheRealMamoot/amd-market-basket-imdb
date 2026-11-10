from argparse import ArgumentParser, Namespace


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(description="Download and prepare IMDb actor baskets.")
    parser.add_argument("--force", action="store_true", help="Download a fresh copy.")
    return parser.parse_args(argv)
