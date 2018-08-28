"""
A stream-friendly text table generator.
"""


CORNER = "+"
PIPE = "|"

LIGHT = "-"
HEAVY = "="


__all__ = ["table_stream"]


def cell(text, width, pad=1, cutoff="..."):
    text = str(text)
    if len(text) > width:
        out = (text[:width - len(cutoff)] + cutoff)[:width]
    else:
        out = text

    padding = " " * pad
    return f"{padding}{out:<{width}}{padding}"


def bar(fill, width):
    assert width >= 2
    return f"{CORNER}{fill * (width - 2)}{CORNER}"


def table_stream(columns, iterable):
    """
    columns:   A list of 2-tuples: (column_name, cell_width)
    iterable:  An iterable of n-tuples of str-able objects
               (where n == len(columns))

    Example:
        >>> columns = [["Id", 5], ["Name", 10]]
        >>> iterable = [[1, "Alex"], [2, "Bob"], [3, "Carol"]]
        >>> gen = table_stream(columns, iterable)
        >>> for row in gen: print(row)
        +--------------------+
        | Id    | Name       |
        +====================+
        | 1     | Alex       |
        | 2     | Bob        |
        | 3     | Carol      |
        +--------------------+
    """

    def rower(row):
        nonlocal columns
        cells = []
        for (text, (_, col_width)) in zip(row, columns):
            cells.append(cell(text, col_width))
        return f"{PIPE}{PIPE.join(cells)}{PIPE}"

    header_row = rower(header for (header, col_width) in columns)
    width = len(header_row)

    yield bar(LIGHT, width)
    yield header_row
    yield bar(HEAVY, width)
    for it in iterable:
        yield(rower(it))
    yield bar(LIGHT, width)
