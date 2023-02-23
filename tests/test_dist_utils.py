from spei.utils import dists_test

from .fixtures import head


def test_dists_test(head) -> None:
    _ = dists_test(head)
