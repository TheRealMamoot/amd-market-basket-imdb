from argparse import ArgumentParser, Namespace


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(description="Find frequent actor groups in IMDb movies.")
    parser.add_argument("--force", action="store_true", help="Download a fresh copy.")
    parser.add_argument(
        "--copies",
        type=int,
        default=1,
        help="Stack the original movie baskets this many times (default: 1).",
    )
    parser.add_argument(
        "--augmentation",
        choices=("plain", "relabeled"),
        default="plain",
        help="plain repeats the baskets and multiplies supports by the number of "
        "copies; relabeled renames actors in each copy and keeps supports fixed "
        "(default: plain).",
    )
    parser.add_argument(
        "--variants",
        choices=("apriori", "apriori_optimized", "pcy"),
        nargs="+",
        default=["apriori", "apriori_optimized", "pcy"],
        help="A-Priori variants compared with exhaustive counting in experiments "
        "and scaling (default: apriori apriori_optimized pcy).",
    )
    parser.add_argument(
        "--buckets",
        type=int,
        nargs="+",
        default=[100_000],
        help="PCY hash buckets; experiments run PCY once per value, single runs "
        "use one value (default: 100000).",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--experiment",
        action="store_true",
        help="Compare exhaustive counting and A-Priori and save runtime measurements.",
    )
    modes.add_argument(
        "--scaling",
        action="store_true",
        help="Compare the algorithms on augmented copies of the original baskets.",
    )
    parser.add_argument(
        "--copy-counts",
        type=int,
        nargs="+",
        default=[1, 10, 50, 100],
        help="Numbers of copies for scaling (default: 1 10 50 100).",
    )
    parser.add_argument(
        "--supports",
        type=int,
        nargs="+",
        default=[2, 3, 5, 10],
        help="Support thresholds on the original movies; plain augmentation "
        "multiplies them by the number of copies (default: 2 3 5 10).",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="Runs per algorithm and threshold in experiments or scaling (default: 3).",
    )
    parser.add_argument(
        "--algorithm",
        choices=("apriori", "apriori-optimized", "pcy", "exhaustive"),
        default="apriori",
        help="Mining algorithm (default: apriori).",
    )
    parser.add_argument(
        "--min-support",
        type=int,
        default=2,
        help="Minimum number of original movies containing an actor group; plain "
        "augmentation multiplies it by --copies (default: 2).",
    )
    args = parser.parse_args(argv)
    if args.scaling and args.copies != 1:
        parser.error("Use --copy-counts instead of --copies with --scaling.")
    if args.copies < 1:
        parser.error("--copies must be at least 1.")
    args.variants = list(dict.fromkeys(args.variants))
    args.buckets = list(dict.fromkeys(args.buckets))
    if any(num_buckets < 1 for num_buckets in args.buckets):
        parser.error("--buckets values must be at least 1.")
    if args.algorithm == "pcy" and len(args.buckets) > 1:
        if not (args.experiment or args.scaling):
            parser.error("A single PCY run takes one --buckets value.")
    if any(copies < 1 for copies in args.copy_counts):
        parser.error("--copy-counts values must be at least 1.")
    if args.min_support < 1:
        parser.error("--min-support must be at least 1.")
    if args.repeats < 1:
        parser.error("--repeats must be at least 1.")
    if any(support < 1 for support in args.supports):
        parser.error("--supports values must be at least 1.")
    return args
