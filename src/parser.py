from argparse import ArgumentParser, Namespace


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(description="Find frequent actor groups in IMDb movies.")
    parser.add_argument("--force", action="store_true", help="Download a fresh copy.")
    parser.add_argument(
        "--experiment",
        action="store_true",
        help="Compare exhaustive counting and A-Priori and save runtime measurements.",
    )
    parser.add_argument(
        "--supports",
        type=int,
        nargs="+",
        default=[2, 3, 5, 10],
        help="Support thresholds for experiments (default: 2 3 5 10).",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Runs per algorithm and threshold in experiments (default: 3).",
    )
    parser.add_argument(
        "--algorithm",
        choices=("apriori", "exhaustive"),
        default="apriori",
        help="Mining algorithm (default: apriori).",
    )
    parser.add_argument(
        "--min-support",
        type=int,
        default=2,
        help="Minimum number of movies containing an actor group (default: 2).",
    )
    args = parser.parse_args(argv)
    if args.min_support < 1:
        parser.error("--min-support must be at least 1.")
    if args.repeats < 1:
        parser.error("--repeats must be at least 1.")
    if any(support < 1 for support in args.supports):
        parser.error("--supports values must be at least 1.")
    return args
