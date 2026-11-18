import csv
import gc
from functools import partial
from pathlib import Path
from time import perf_counter

from src.apriori import apriori
from src.config import RESULTS_DIR
from src.exhaustive import count_exhaustive
from src.pcy import DEFAULT_BUCKETS, pcy
from src.stacking import (
    AUGMENTATIONS,
    augment_baskets,
    augmented_support,
    expected_itemsets,
)

VARIANTS = ("apriori", "apriori_optimized", "pcy")


def exhaustive_with_stats(baskets, min_support, stats=None):
    return count_exhaustive(baskets, min_support)


def build_algorithms(variants, buckets):
    algorithms = [("exhaustive", 0, exhaustive_with_stats)]
    for name in variants:
        if name == "apriori":
            algorithms.append((name, 0, apriori))
        elif name == "apriori_optimized":
            algorithms.append((name, 0, partial(apriori, optimized=True)))
        elif name == "pcy":
            for num_buckets in buckets:
                algorithms.append(
                    (name, num_buckets, partial(pcy, num_buckets=num_buckets))
                )
        else:
            raise ValueError(f"Unknown A-Priori variant: {name}.")
    return algorithms


def run_experiments(
    baskets,
    support_values,
    repeats=3,
    variants=None,
    buckets=(DEFAULT_BUCKETS,),
    warmup=True,
    verbose=True,
):
    if variants is None:
        variants = list(VARIANTS)
    if not variants:
        raise ValueError("Provide at least one A-Priori variant.")
    if "pcy" in variants:
        if not buckets:
            raise ValueError("Provide at least one number of PCY buckets.")
        for num_buckets in buckets:
            if num_buckets < 1:
                raise ValueError("Number of buckets must be at least 1.")
    if repeats < 1:
        raise ValueError("Repeats must be at least 1.")
    if not support_values:
        raise ValueError("Provide at least one support threshold.")
    for support in support_values:
        if support < 1:
            raise ValueError("Minimum support must be at least 1.")

    algorithms = build_algorithms(variants, buckets)
    measurements = []

    for support in support_values:
        if warmup:
            for name, num_buckets, algorithm in algorithms:
                algorithm(baskets, support, stats={})

        for repeat in range(1, repeats + 1):
            outputs = {}
            current_measurements = []
            run_order = algorithms.copy()
            if repeat % 2 == 0:
                run_order.reverse()

            for name, num_buckets, algorithm in run_order:
                stats = {}
                gc.collect()
                gc.disable()
                try:
                    start = perf_counter()
                    result = algorithm(baskets, support, stats=stats)
                    elapsed = perf_counter() - start
                finally:
                    gc.enable()
                outputs[(name, num_buckets)] = result
                pair_counters = ""
                larger_candidates = ""
                if name != "exhaustive":
                    counters = stats.get("counters", {})
                    pair_counters = counters.get(2, 0)
                    larger_candidates = 0
                    for size, count in counters.items():
                        if size > 2:
                            larger_candidates += count

                current_measurements.append(
                    {
                        "movies": len(baskets),
                        "min_support": support,
                        "repeat": repeat,
                        "algorithm": name,
                        "buckets": num_buckets if name == "pcy" else "",
                        "runtime_seconds": elapsed,
                        "frequent_itemsets": len(result),
                        "pair_counters": pair_counters,
                        "larger_candidates": larger_candidates,
                        "frequent_buckets": stats.get("frequent_buckets", ""),
                        "results_match": True,
                    }
                )

            expected = outputs[("exhaustive", 0)]
            for (name, num_buckets), result in outputs.items():
                if result != expected:
                    label = name if name != "pcy" else f"pcy with {num_buckets} buckets"
                    raise RuntimeError(
                        f"{label} disagrees with exhaustive counting at support "
                        f"{support}, repeat {repeat}."
                    )

            measurements.extend(current_measurements)
            if verbose:
                print(f"Support {support}, repeat {repeat}/{repeats}: results match.")

    return measurements


def run_scaling_experiments(
    source_baskets,
    copy_counts,
    base_supports,
    repeats=3,
    augmentation="plain",
    variants=None,
    buckets=(DEFAULT_BUCKETS,),
    warmup=True,
    verbose=True,
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
        if verbose:
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

            rows = run_experiments(
                baskets,
                [min_support],
                repeats,
                variants,
                buckets,
                warmup=warmup,
                verbose=verbose,
            )
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
