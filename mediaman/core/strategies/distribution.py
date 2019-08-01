
import copy
from typing import Mapping, Set

import sortedcontainers


class Obj:
    def __init__(self, id, n):
        self.id = id
        self.n = n

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id}, {human_bytes(self.n)})"


class Bin(Obj):
    pass


class Item(Obj):
    pass


def human_bytes(n):
    """Return the given bytes as a human-friendly string"""

    step = 1000
    abbrevs = ['KB', 'MB', 'GB', 'TB']

    if n < step:
        return f"{n}B"

    for abbrev in abbrevs:
        n /= step
        if n < step:
            break

    return f"{n:.2f}{abbrev}"


def fast_optimal(
        bins: Mapping[str, int],
        items: Mapping[str, int],
        distribution: Mapping[str, Set[str]]=None):
    """
    Assign a near-optimal distribution of items to bins, quickly.

    @param bins Mapping of bin identifier to bin size
    @param items Mapping of item identifier to item size
    @return distribution Mapping of bin identifier to set of item identifiers
    """

    distribution = {k: set() for k in bins} if not distribution else distribution

    bin_queue = sortedcontainers.SortedList(key=lambda bin: bin.n)
    bin_queue.update(Bin(k, v) for k, v in bins.items())
    # print(bin_queue)

    items_queue = sorted((Item(k, v) for k, v in items.items()), key=lambda item: item.n)
    # print(items_queue)

    while items_queue:
        no_change = True
        trim_items = 0

        if items_queue[0].n > bin_queue[-1].n:
            print(f"All remaining items too large for bins.")
            # print(items_queue[0], bin_queue[-1])
            break

        for item in reversed(items_queue):

            # find smallest bin larger than item
            for index in range(bin_queue.bisect_left(item), len(bin_queue)):
                if item.id not in distribution[bin_queue[index].id]:
                    bin = bin_queue.pop(index)
                    break
            else:
                # item is too large for any bin
                # (that doesn't already have it)
                no_change = False
                trim_items += 1
                continue

            if item.id not in distribution[bin.id]:
                distribution[bin.id].add(item.id)
                bin = Bin(bin.id, bin.n - item.n)
                no_change = False

            bin_queue.add(bin)

        if no_change:
            break

        if trim_items:
            items_queue = items_queue[:-trim_items]

    return distribution


def distribute(bins, items, distribution=None):
    bins = copy.deepcopy(bins)
    items = copy.deepcopy(items)
    if distribution is not None:
        distribution = copy.deepcopy(distribution)

    total = []

    total_size = sum(size for size in items.values())
    print(f"total file size (sum): {human_bytes(total_size)}")

    for (bin_id, bin_cap) in list(bins.items()):
        if bin_cap >= total_size:
            print(f"Bin {bin_id, human_bytes(bin_cap)} can fit all items.")
            bin = (bin_id, bin_cap - total_size)
            total.append(bin)
            del bins[bin_id]
            del distribution[bin_id]
    # print(list((bin_id, human_bytes(bin_cap)) for bin_id, bin_cap in total))

    if not bins:
        print("distribution not necessary!")
        return

    dist = fast_optimal(bins, items, distribution=distribution)
    dist.update({bin[0]: set(items) for bin in total})
    # print(dist)

    pres = {f: sum((f in v) for v in dist.values()) for f in items}
    # print(pres)

    redundancy = min(pres.values())
    availability = (sum(pres.values()) / len(pres))

    print(f"redundancy: {redundancy}")
    print(f"availability: {availability}")
    # print(f"No presence: {list((i, items[i]) for (i, v) in pres.items() if not v)}")

    return dist


def test():
    # distribute({'drive': 10, 'local': 20, 'net': 200}, {'a': 113, 'b': 118, 'c': 25, 'd': 4, 'e': 4, 'f': 6})
    import random
    KB = 1024**1
    MB = 1024**2
    GB = 1024**3

    import cProfile
    profile = cProfile.Profile()
    profile.disable()

    bins = {'net': 400 * GB, 'drive': 100 * GB, 'local': 20 * GB, 'dropbox': 20 * GB, 'b1': 20 * GB, 'b2': 20 * GB, 'b3': 20 * GB}
    items = {str(random.random()): random.randint(1 * KB, 1 * MB) for i in range(100000)}

    # profile.enable()
    distribute(bins, items)
    profile.disable()

    # profile.print_stats()

    # distribute(
    #     dict(zip('123', (5, 11, 23))),
    #     dict(zip('ABCD', (2, 4, 8, 16))))
