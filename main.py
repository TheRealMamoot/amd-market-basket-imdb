from collections import Counter
from pprint import pprint

from src.apriori import apriori
from src.data import download_dataset
from src.exhaustive import count_exhaustive
from src.experiments import run_experiments, save_results
from src.parser import parse_args
from src.preprocessing import build_baskets, inspect_actors, load_movies


def main() -> None:
    args = parse_args()
    dataset_path = download_dataset(force=args.force)
    print(f"Dataset ready: {dataset_path}")
    movies = load_movies(dataset_path)
    pprint(inspect_actors(movies), sort_dicts=False)
    baskets = build_baskets(movies)
    print(f"Prepared {len(baskets)} baskets.")
    if args.experiment:
        measurements = run_experiments(baskets, args.supports, args.repeats)
        results_path = save_results(measurements)
        print(f"Experiment results saved: {results_path}")
        return

    if args.algorithm == "apriori":
        frequent_itemsets = apriori(baskets, args.min_support)
    else:
        frequent_itemsets = count_exhaustive(baskets, args.min_support)
    print(f"Found {len(frequent_itemsets)} frequent itemsets.")
    print("Ten most frequent itemsets:")
    pprint(Counter(frequent_itemsets).most_common(10))


if __name__ == "__main__":
    main()
