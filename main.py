from pprint import pprint

from src.data import download_dataset
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


if __name__ == "__main__":
    main()
