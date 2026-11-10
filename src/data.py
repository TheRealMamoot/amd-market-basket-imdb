import os
from pathlib import Path
from tempfile import TemporaryDirectory

from dotenv import load_dotenv

from src.config import DATA_DIR, DATASET_FILENAME, DATASET_ID, ENV_PATH


def download_dataset(data_dir: Path = DATA_DIR, force: bool = False) -> Path:
    data_dir = Path(data_dir).resolve()
    dataset_path = data_dir / DATASET_FILENAME

    if dataset_path.is_file() and dataset_path.stat().st_size > 0 and not force:
        return dataset_path

    load_dotenv(ENV_PATH)
    if not os.environ.get("KAGGLE_API_TOKEN", "").strip():
        raise ValueError(
            "Set KAGGLE_API_TOKEN in the project .env file or environment."
        )

    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    data_dir.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(dir=data_dir) as temporary_dir:
        download_dir = Path(temporary_dir)
        api.dataset_download_files(
            DATASET_ID,
            path=str(download_dir),
            unzip=True,
            quiet=True,
        )
        downloaded_path = download_dir / DATASET_FILENAME
        if not downloaded_path.is_file() or downloaded_path.stat().st_size == 0:
            raise FileNotFoundError(
                f"Kaggle download did not contain a nonempty {DATASET_FILENAME}."
            )
        downloaded_path.replace(dataset_path)

    return dataset_path
