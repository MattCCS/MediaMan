
from typing import Mapping

from mediaman.distribution import Bin, Item


def fast_serpent(bins: Mapping[str, int], items: Mapping[str, int]):
    """
    Assign a poor distribution of items to bins, very quickly.

    @param bins Mapping of bin identifier to bin size
    @param items Mapping of item identifier to item size
    @return distribution Mapping of bin identifier to set of item identifiers
    """

    distribution = {k: set() for k in bins}
    range_distribution = {k: set() for k in bins}

    bin_queue = [Bin(k, v) for k, v in bins.items()]
    print(bin_queue)

    items_queue = sorted((Item(k, v) for k, v in items.items()), key=lambda item: item.n)

    step = len(bin_queue)
    total = len(items_queue)
    start_offset = -1

    for start_offset in range(step):

        for bin in bin_queue:
            item_range = range(start_offset, total, step)

            for i in item_range:
                item = items_queue[i]
                if item.n > bin.n:
                    # print(f"{item} can't fit in {bin}")
                    break
                bin.n -= item.n

            range_distribution[bin.id].add(range(start_offset, i, step))

    print(bin_queue)
    print(range_distribution)
    for (bin_id, ranges) in range_distribution.items():
        items = set(items_queue[i].id for range in ranges for i in range)
        distribution[bin_id].update(items)

    return distribution
