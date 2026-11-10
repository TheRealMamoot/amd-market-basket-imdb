from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
DATA_DIR = PROJECT_ROOT / "data"
DATASET_ID = "harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows"
DATASET_FILENAME = "imdb_top_1000.csv"
