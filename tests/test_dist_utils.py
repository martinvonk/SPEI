from numpy import random

from spei.utils import dists_test

from .fixtures import head


def test_dists_test(head):
    _ = dists_test(head)
