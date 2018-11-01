"""
Module for misc utils
"""


def grouper(lst, n):
    """
    Split lst into chunks of at most n elements

    Parameters
    ----------
    lst : list
    n : int

    Examples
    --------
    >>> grouper([11, 12, 13, 14], 1)
    [[11], [12], [13], [14]]

    >>> grouper([11, 12, 13, 14], 2)
    [[11, 12], [13, 14]]

    >>> grouper([11, 12, 13, 14], 3)
    [[11, 12, 13], [14]]

    >>> grouper([11, 12, 13, 14], 4)
    [[11, 12, 13, 14]]

    >>> grouper([11, 12, 13, 14], 100)
    [[11, 12, 13, 14]]
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]
