AUGMENTATIONS = ("plain", "relabeled")


def _check_copies(copies):
    if copies < 1:
        raise ValueError("Number of copies must be at least 1.")


def _check_augmentation(augmentation):
    if augmentation not in AUGMENTATIONS:
        raise ValueError(f"Augmentation must be one of: {', '.join(AUGMENTATIONS)}.")


def stack_baskets(
    baskets: list[tuple[str, ...]], copies: int
) -> list[tuple[str, ...]]:
    _check_copies(copies)
    return list(baskets) * copies


def scale_counts(
    itemsets: dict[tuple[str, ...], int], copies: int
) -> dict[tuple[str, ...], int]:
    _check_copies(copies)
    scaled = {}
    for group, count in itemsets.items():
        scaled[group] = count * copies
    return scaled


def relabel_actor(actor: str, copy: int) -> str:
    if copy == 1:
        return actor
    return f"{actor}#{copy}"


def relabel_group(group: tuple[str, ...], copy: int) -> tuple[str, ...]:
    renamed = []
    for actor in group:
        renamed.append(relabel_actor(actor, copy))
    return tuple(sorted(renamed))


def relabel_baskets(
    baskets: list[tuple[str, ...]], copies: int
) -> list[tuple[str, ...]]:
    _check_copies(copies)
    relabeled = []
    for copy in range(1, copies + 1):
        for basket in baskets:
            relabeled.append(relabel_group(basket, copy))
    return relabeled


def relabel_counts(
    itemsets: dict[tuple[str, ...], int], copies: int
) -> dict[tuple[str, ...], int]:
    _check_copies(copies)
    relabeled = {}
    for copy in range(1, copies + 1):
        for group, count in itemsets.items():
            relabeled[relabel_group(group, copy)] = count
    return relabeled


def augment_baskets(
    baskets: list[tuple[str, ...]], copies: int, augmentation: str = "plain"
) -> list[tuple[str, ...]]:
    _check_augmentation(augmentation)
    if augmentation == "plain":
        return stack_baskets(baskets, copies)
    return relabel_baskets(baskets, copies)


def augmented_support(base_support: int, copies: int, augmentation: str = "plain") -> int:
    _check_copies(copies)
    _check_augmentation(augmentation)
    if augmentation == "plain":
        return base_support * copies
    return base_support


def expected_itemsets(
    itemsets: dict[tuple[str, ...], int], copies: int, augmentation: str = "plain"
) -> dict[tuple[str, ...], int]:
    _check_augmentation(augmentation)
    if augmentation == "plain":
        return scale_counts(itemsets, copies)
    return relabel_counts(itemsets, copies)
