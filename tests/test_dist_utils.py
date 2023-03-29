from pandas import Series

from spei.utils import dists_test


def test_dists_test(head: Series) -> None:
    _ = dists_test(head)
