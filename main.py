from collections import Counter
from pprint import pprint

from src.apriori import apriori
from src.config import RESULTS_DIR
from src.data import download_dataset
from src.exhaustive import count_exhaustive
from src.experiments import run_experiments, run_scaling_experiments, save_results
from src.parser import parse_args
from src.pcy import pcy
from src.preprocessing import build_baskets, inspect_actors, load_movies
from src.stacking import augment_baskets, augmented_support


def main() -> None:
    args = parse_args()
    dataset_path = download_dataset(force=args.force)
    print(f"Dataset ready: {dataset_path}")
    movies = load_movies(dataset_path)
    pprint(inspect_actors(movies), sort_dicts=False)
    baskets = build_baskets(movies)
    print(f"Prepared {len(baskets)} baskets.")
    if args.scaling:
        measurements = run_scaling_experiments(
            baskets,
            args.copy_counts,
            args.supports,
            args.repeats,
            args.augmentation,
            args.variants,
            args.buckets,
        )
        path = RESULTS_DIR / f"scaling_{args.augmentation}.csv"
        results_path = save_results(measurements, path)
        print(f"Scaling results saved: {results_path}")
        return

    original_movies = len(baskets)
    if args.copies > 1:
        baskets = augment_baskets(baskets, args.copies, args.augmentation)
        print(
            f"Added {args.copies} {args.augmentation} copies; "
            f"total baskets: {len(baskets)}."
        )

    if args.experiment:
        supports = []
        for support in args.supports:
            supports.append(augmented_support(support, args.copies, args.augmentation))
        measurements = run_experiments(
            baskets, supports, args.repeats, args.variants, args.buckets
        )
        for row in measurements:
            row["augmentation"] = args.augmentation
            row["copies"] = args.copies
            row["original_movies"] = original_movies
            row["base_support"] = row["min_support"]
            if args.augmentation == "plain":
                row["base_support"] = row["min_support"] // args.copies
        path = RESULTS_DIR / "algorithm_comparison.csv"
        if args.copies > 1:
            path = (
                RESULTS_DIR
                / f"algorithm_comparison_{args.augmentation}_{args.copies}.csv"
            )
        results_path = save_results(measurements, path)
        print(f"Experiment results saved: {results_path}")
        return

    min_support = augmented_support(args.min_support, args.copies, args.augmentation)
    stats = {}
    if args.algorithm == "apriori":
        frequent_itemsets = apriori(baskets, min_support, stats=stats)
    elif args.algorithm == "apriori-optimized":
        frequent_itemsets = apriori(baskets, min_support, optimized=True, stats=stats)
    elif args.algorithm == "pcy":
        frequent_itemsets = pcy(baskets, min_support, args.buckets[0], stats=stats)
    else:
        frequent_itemsets = count_exhaustive(baskets, min_support)
    if stats:
        print(f"Counters per itemset size: {stats.get('counters', {})}")
    if "frequent_buckets" in stats:
        print(f"Frequent buckets: {stats['frequent_buckets']} of {stats['buckets']}")
    print(f"Found {len(frequent_itemsets)} frequent itemsets.")
    print("Ten most frequent itemsets:")
    pprint(Counter(frequent_itemsets).most_common(10))


if __name__ == "__main__":
    main()
