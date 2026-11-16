def stack_baskets(
    baskets: list[tuple[str, ...]], copies: int
) -> list[tuple[str, ...]]:
    if copies < 1:
        raise ValueError("Number of copies must be at least 1.")
    return list(baskets) * copies


def scale_counts(
    itemsets: dict[tuple[str, ...], int], copies: int
) -> dict[tuple[str, ...], int]:
    if copies < 1:
        raise ValueError("Number of copies must be at least 1.")
    scaled = {}
    for group, count in itemsets.items():
        scaled[group] = count * copies
    return scaled
