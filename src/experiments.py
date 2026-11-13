import csv
from pathlib import Path
from time import perf_counter

from src.apriori import apriori
from src.config import RESULTS_DIR
from src.exhaustive import count_exhaustive


def run_experiments(baskets, support_values, repeats=3):
    if repeats < 1:
        raise ValueError("Repeats must be at least 1.")
    if not support_values:
        raise ValueError("Provide at least one support threshold.")
    for support in support_values:
        if support < 1:
            raise ValueError("Minimum support must be at least 1.")

    algorithms = [("exhaustive", count_exhaustive), ("apriori", apriori)]
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

            if outputs["exhaustive"] != outputs["apriori"]:
                raise RuntimeError(
                    f"Algorithms disagree at support {support}, repeat {repeat}."
                )

            measurements.extend(current_measurements)
            print(f"Support {support}, repeat {repeat}/{repeats}: results match.")

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
