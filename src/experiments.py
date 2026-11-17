import csv
from functools import partial
from pathlib import Path
from time import perf_counter

from src.apriori import apriori
from src.config import RESULTS_DIR
from src.exhaustive import count_exhaustive
from src.stacking import (
    AUGMENTATIONS,
    augment_baskets,
    augmented_support,
    expected_itemsets,
)

APRIORI_VARIANTS = {
    "apriori": apriori,
    "apriori_optimized": partial(apriori, optimized=True),
}


def run_experiments(baskets, support_values, repeats=3, variants=None):
    if variants is None:
        variants = list(APRIORI_VARIANTS)
    if not variants:
        raise ValueError("Provide at least one A-Priori variant.")
    for name in variants:
        if name not in APRIORI_VARIANTS:
            raise ValueError(f"Unknown A-Priori variant: {name}.")
    if repeats < 1:
        raise ValueError("Repeats must be at least 1.")
    if not support_values:
        raise ValueError("Provide at least one support threshold.")
    for support in support_values:
        if support < 1:
            raise ValueError("Minimum support must be at least 1.")

    algorithms = [("exhaustive", count_exhaustive)]
    for name in variants:
        algorithms.append((name, APRIORI_VARIANTS[name]))
    measurements = []

    for support in support_values:
        for repeat in range(1, repeats + 1):
            outputs = {}
            current_measurements = []
            run_order = algorithms.copy()
            if repeat % 2 == 0:
                run_order.reverse()

            for name, algorithm in run_order:
                start = perf_counter()
                result = algorithm(baskets, support)
                elapsed = perf_counter() - start
                outputs[name] = result
                current_measurements.append(
                    {
                        "movies": len(baskets),
                        "min_support": support,
                        "repeat": repeat,
                        "algorithm": name,
                        "runtime_seconds": elapsed,
                        "frequent_itemsets": len(result),
                        "results_match": True,
                    }
                )

            for name, result in outputs.items():
                if result != outputs["exhaustive"]:
                    raise RuntimeError(
                        f"{name} disagrees with exhaustive counting at support "
                        f"{support}, repeat {repeat}."
                    )

            measurements.extend(current_measurements)
            print(f"Support {support}, repeat {repeat}/{repeats}: results match.")

    return measurements


def run_scaling_experiments(
    source_baskets,
    copy_counts,
    base_supports,
    repeats=3,
    augmentation="plain",
    variants=None,
):
    if not source_baskets:
        raise ValueError("Provide original movie baskets.")
    if augmentation not in AUGMENTATIONS:
        raise ValueError(f"Augmentation must be one of: {', '.join(AUGMENTATIONS)}.")
    if not copy_counts:
        raise ValueError("Provide at least one number of copies.")
    for copies in copy_counts:
        if copies < 1:
            raise ValueError("Number of copies must be at least 1.")
    if not base_supports:
        raise ValueError("Provide at least one support threshold.")
    for support in base_supports:
        if support < 1:
            raise ValueError("Minimum support must be at least 1.")
    if repeats < 1:
        raise ValueError("Repeats must be at least 1.")

    original_results = {}
    for support in base_supports:
        original_results[support] = count_exhaustive(source_baskets, support)

    support_rule = "fraction" if augmentation == "plain" else "count"
    measurements = []
    for copies in copy_counts:
        baskets = augment_baskets(source_baskets, copies, augmentation)
        print(
            f"Scaling dataset: {len(baskets)} baskets "
            f"({copies} {augmentation} copies)."
        )

        for base_support in base_supports:
            min_support = augmented_support(base_support, copies, augmentation)
            expected = expected_itemsets(
                original_results[base_support], copies, augmentation
            )
            if count_exhaustive(baskets, min_support) != expected:
                raise RuntimeError(
                    f"Augmented results differ from the expected ones at {copies} "
                    f"{augmentation} copies, support {base_support}."
                )

            rows = run_experiments(baskets, [min_support], repeats, variants)
            for row in rows:
                row["augmentation"] = augmentation
                row["support_rule"] = support_rule
                row["copies"] = copies
                row["original_movies"] = len(source_baskets)
                row["base_support"] = base_support
                row["support_fraction"] = min_support / len(baskets)
                row["matches_expected"] = True
            measurements.extend(rows)

    return measurements


def save_results(
    measurements, path: Path = RESULTS_DIR / "algorithm_comparison.csv"
) -> Path:
    if not measurements:
        raise ValueError("No experiment measurements to save.")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(measurements[0]))
        writer.writeheader()
        writer.writerows(measurements)

    return path
