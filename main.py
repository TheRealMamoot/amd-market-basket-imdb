from collections import Counter
from pprint import pprint

from src.apriori import apriori
from src.config import RESULTS_DIR
from src.data import download_dataset
from src.exhaustive import count_exhaustive
from src.experiments import run_experiments, run_scaling_experiments, save_results
from src.parser import parse_args
from src.preprocessing import build_baskets, inspect_actors, load_movies
from src.stacking import stack_baskets


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
            baskets, args.copy_counts, args.supports, args.repeats
        )
        results_path = save_results(measurements, RESULTS_DIR / "scaling_stacked.csv")
        print(f"Scaling results saved: {results_path}")
        return

    original_movies = len(baskets)
    if args.copies > 1:
        baskets = stack_baskets(baskets, args.copies)
        print(f"Stacked {args.copies} copies; total baskets: {len(baskets)}.")

    if args.experiment:
        supports = [support * args.copies for support in args.supports]
        measurements = run_experiments(baskets, supports, args.repeats)
        for row in measurements:
            row["copies"] = args.copies
            row["original_movies"] = original_movies
            row["base_support"] = row["min_support"] // args.copies
        path = RESULTS_DIR / "algorithm_comparison.csv"
        if args.copies > 1:
            path = RESULTS_DIR / f"algorithm_comparison_stacked_{args.copies}.csv"
        results_path = save_results(measurements, path)
        print(f"Experiment results saved: {results_path}")
        return

    min_support = args.min_support * args.copies
    if args.algorithm == "apriori":
        frequent_itemsets = apriori(baskets, min_support)
    else:
        frequent_itemsets = count_exhaustive(baskets, min_support)
    print(f"Found {len(frequent_itemsets)} frequent itemsets.")
    print("Ten most frequent itemsets:")
    pprint(Counter(frequent_itemsets).most_common(10))


if __name__ == "__main__":
    main()
