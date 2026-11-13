from collections import Counter
from itertools import combinations


def find_frequent_singles(baskets, min_support):
    counts = Counter()

    for basket in baskets:
        for actor in basket:
            counts[(actor,)] += 1

    frequent = {}
    for group, count in counts.items():
        if count >= min_support:
            frequent[group] = count

    return frequent


def generate_candidates(frequent, size):
    previous_groups = sorted(frequent)
    previous_set = set(previous_groups)
    candidates = set()

    for left, right in combinations(previous_groups, 2):
        if left[: size - 2] != right[: size - 2]:
            continue

        candidate = tuple(sorted(set(left) | set(right)))
        if len(candidate) != size:
            continue

        keep = True
        for subset in combinations(candidate, size - 1):
            if subset not in previous_set:
                keep = False
                break

        if keep:
            candidates.add(candidate)

    return candidates


def count_candidates(baskets, candidates, min_support):
    counts = Counter()

    for basket in baskets:
        basket_set = set(basket)
        for candidate in candidates:
            if basket_set.issuperset(candidate):
                counts[candidate] += 1

    frequent = {}
    for candidate, count in counts.items():
        if count >= min_support:
            frequent[candidate] = count

    return frequent


def apriori(
    baskets: list[tuple[str, ...]], min_support: int
) -> dict[tuple[str, ...], int]:
    if min_support < 1:
        raise ValueError("Minimum support must be at least 1.")

    frequent = find_frequent_singles(baskets, min_support)
    results = frequent.copy()
    size = 2

    largest_basket = 0
    for basket in baskets:
        largest_basket = max(largest_basket, len(basket))

    while frequent and size <= largest_basket:
        candidates = generate_candidates(frequent, size)
        if not candidates:
            break

        frequent = count_candidates(baskets, candidates, min_support)
        results.update(frequent)
        size += 1

    return results
