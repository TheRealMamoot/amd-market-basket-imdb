from collections import Counter
from itertools import combinations


def count_exhaustive(
    baskets: list[tuple[str, ...]], min_support: int
) -> dict[tuple[str, ...], int]:
    if min_support < 1:
        raise ValueError("Minimum support must be at least 1.")

    counts = Counter()

    for basket in baskets:
        for size in range(1, len(basket) + 1):
            for group in combinations(basket, size):
                counts[group] += 1

    frequent_itemsets = {}
    for group, count in counts.items():
        if count >= min_support:
            frequent_itemsets[group] = count

    return frequent_itemsets
