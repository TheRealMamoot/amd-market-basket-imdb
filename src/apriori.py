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


def generate_candidates_by_prefix(frequent, size):
    previous_set = set(frequent)
    groups_by_prefix = {}
    for group in sorted(frequent):
        groups_by_prefix.setdefault(group[:-1], []).append(group)

    candidates = set()
    for members in groups_by_prefix.values():
        for left, right in combinations(members, 2):
            candidate = left + (right[-1],)

            keep = True
            for subset in combinations(candidate, size - 1):
                if subset not in previous_set:
                    keep = False
                    break

            if keep:
                candidates.add(candidate)

    return candidates


def frequent_actors(frequent):
    actors = set()
    for group in frequent:
        actors.update(group)
    return actors


def trim_basket(basket, actors):
    kept = []
    for actor in basket:
        if actor in actors:
            kept.append(actor)
    return kept


def count_frequent_pairs(baskets, actors, min_support):
    counts = Counter()

    for basket in baskets:
        for pair in combinations(trim_basket(basket, actors), 2):
            counts[pair] += 1

    frequent = {}
    for pair, count in counts.items():
        if count >= min_support:
            frequent[pair] = count

    return frequent, len(counts)


def record_counters(stats, size, counters):
    if stats is not None:
        stats.setdefault("counters", {})[size] = counters


def count_candidates(baskets, candidates, min_support, actors=None):
    counts = Counter()

    if not candidates:
        return {}

    size = len(next(iter(candidates)))

    for basket in baskets:
        if actors is not None:
            basket = trim_basket(basket, actors)
        for group in combinations(basket, size):
            if group in candidates:
                counts[group] += 1

    frequent = {}
    for candidate, count in counts.items():
        if count >= min_support:
            frequent[candidate] = count

    return frequent


def apriori(
    baskets: list[tuple[str, ...]],
    min_support: int,
    optimized: bool = False,
    stats: dict | None = None,
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
        if optimized:
            actors = frequent_actors(frequent)
            if size == 2:
                frequent, counted = count_frequent_pairs(baskets, actors, min_support)
                record_counters(stats, size, counted)
            else:
                candidates = generate_candidates_by_prefix(frequent, size)
                if not candidates:
                    break
                record_counters(stats, size, len(candidates))
                frequent = count_candidates(baskets, candidates, min_support, actors)
        else:
            candidates = generate_candidates(frequent, size)
            if not candidates:
                break
            record_counters(stats, size, len(candidates))
            frequent = count_candidates(baskets, candidates, min_support)

        results.update(frequent)
        size += 1

    return results
