from collections import Counter
from pathlib import Path

import pandas as pd

ACTOR_COLUMNS = ("Star1", "Star2", "Star3", "Star4")


def _actor_columns(movies: pd.DataFrame) -> pd.DataFrame:
    missing = []
    for column in ACTOR_COLUMNS:
        if column not in movies.columns:
            missing.append(column)

    if missing:
        raise ValueError(f"Missing actor columns: {', '.join(sorted(missing))}")
    return movies.loc[:, list(ACTOR_COLUMNS)]


def _clean_actor(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def load_movies(path: Path) -> pd.DataFrame:
    movies = pd.read_csv(
        Path(path),
        encoding="utf-8-sig",
        keep_default_na=False,
        dtype={column: "string" for column in ACTOR_COLUMNS},
    )
    _actor_columns(movies)
    return movies


def build_baskets(movies: pd.DataFrame) -> list[tuple[str, ...]]:
    actors = _actor_columns(movies)
    baskets = []

    for row in actors.itertuples(index=False, name=None):
        basket = set()
        for value in row:
            name = _clean_actor(value)
            if name:
                basket.add(name)
        baskets.append(tuple(sorted(basket)))

    return baskets


def inspect_actors(movies: pd.DataFrame) -> dict[str, object]:
    actors = _actor_columns(movies)
    missing_names = dict.fromkeys(ACTOR_COLUMNS, 0)
    blank_names = dict.fromkeys(ACTOR_COLUMNS, 0)
    names_with_whitespace = dict.fromkeys(ACTOR_COLUMNS, 0)
    distinct_actors = set()
    basket_sizes = Counter()
    movies_with_repeated_actors = 0
    duplicate_actor_entries_removed = 0

    for row in actors.itertuples(index=False, name=None):
        names = []
        for column, value in zip(ACTOR_COLUMNS, row):
            if pd.isna(value):
                missing_names[column] += 1
                continue

            name = _clean_actor(value)
            if isinstance(value, str) and value != name:
                names_with_whitespace[column] += 1

            if name:
                names.append(name)
            else:
                blank_names[column] += 1

        basket = set(names)
        duplicates = len(names) - len(basket)
        if duplicates > 0:
            movies_with_repeated_actors += 1
            duplicate_actor_entries_removed += duplicates

        distinct_actors.update(basket)
        basket_sizes[len(basket)] += 1

    return {
        "movies": len(movies),
        "missing_names": missing_names,
        "blank_names": blank_names,
        "names_with_whitespace": names_with_whitespace,
        "movies_with_repeated_actors": movies_with_repeated_actors,
        "duplicate_actor_entries_removed": duplicate_actor_entries_removed,
        "distinct_actors": len(distinct_actors),
        "empty_baskets": basket_sizes[0],
        "basket_sizes": dict(sorted(basket_sizes.items())),
    }
