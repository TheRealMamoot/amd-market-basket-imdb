from argparse import ArgumentParser

from src.data import download_dataset


def main() -> None:
    parser = ArgumentParser(description="Download the IMDb market-basket dataset.")
    parser.add_argument("--force", action="store_true", help="Download a fresh copy.")
    args = parser.parse_args()
    dataset_path = download_dataset(force=args.force)
    print(f"Dataset ready: {dataset_path}")


if __name__ == "__main__":
    main()
