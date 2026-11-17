from collections import Counter
from itertools import combinations

from src.apriori import (
    count_candidates,
    frequent_actors,
    generate_candidates_by_prefix,
    record_counters,
    trim_basket,
)

DEFAULT_BUCKETS = 100_000
HASH_MULTIPLIER = 2_654_435_761


def bucket_of(left_id, right_id, num_buckets):
    return (left_id * HASH_MULTIPLIER + right_id) % num_buckets


def first_pass(baskets, num_buckets):
    actor_counts = Counter()
    actor_ids = {}
    bucket_counts = [0] * num_buckets

    for basket in baskets:
        ids = []
        for actor in basket:
            actor_counts[actor] += 1
            if actor not in actor_ids:
                actor_ids[actor] = len(actor_ids)
            ids.append(actor_ids[actor])

        for left_id, right_id in combinations(ids, 2):
            bucket_counts[bucket_of(left_id, right_id, num_buckets)] += 1

    return actor_counts, actor_ids, bucket_counts


def frequent_bucket_bitmap(bucket_counts, min_support):
    bitmap = bytearray(len(bucket_counts))
    for bucket, count in enumerate(bucket_counts):
        if count >= min_support:
            bitmap[bucket] = 1
    return bitmap


def count_pcy_pairs(baskets, actors, actor_ids, bitmap, min_support):
    counts = Counter()
    num_buckets = len(bitmap)

    for basket in baskets:
        for left, right in combinations(trim_basket(basket, actors), 2):
            bucket = bucket_of(actor_ids[left], actor_ids[right], num_buckets)
            if bitmap[bucket]:
                counts[(left, right)] += 1

    frequent = {}
    for pair, count in counts.items():
        if count >= min_support:
            frequent[pair] = count

    return frequent, len(counts)


def pcy(
    baskets: list[tuple[str, ...]],
    min_support: int,
    num_buckets: int = DEFAULT_BUCKETS,
    stats: dict | None = None,
) -> dict[tuple[str, ...], int]:
    if min_support < 1:
        raise ValueError("Minimum support must be at least 1.")
    if num_buckets < 1:
        raise ValueError("Number of buckets must be at least 1.")

    actor_counts, actor_ids, bucket_counts = first_pass(baskets, num_buckets)
    bitmap = frequent_bucket_bitmap(bucket_counts, min_support)
    if stats is not None:
        stats["buckets"] = num_buckets
        stats["frequent_buckets"] = sum(bitmap)

    frequent = {}
    for actor, count in actor_counts.items():
        if count >= min_support:
            frequent[(actor,)] = count
    results = frequent.copy()

    largest_basket = 0
    for basket in baskets:
        largest_basket = max(largest_basket, len(basket))

    if not frequent or largest_basket < 2:
        return results

    actors = frequent_actors(frequent)
    frequent, counted = count_pcy_pairs(
        baskets, actors, actor_ids, bitmap, min_support
    )
    record_counters(stats, 2, counted)
    results.update(frequent)
    size = 3

    while frequent and size <= largest_basket:
        actors = frequent_actors(frequent)
        candidates = generate_candidates_by_prefix(frequent, size)
        if not candidates:
            break
        record_counters(stats, size, len(candidates))
        frequent = count_candidates(baskets, candidates, min_support, actors)
        results.update(frequent)
        size += 1

    return results
