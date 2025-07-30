import pytest
from autotuner_core.algorithms.sorting.merge_sort import merge_sort, merge

@pytest.mark.parametrize("input_list,expected", [
    ([], []),
    ([1], [1]),
    ([3, 2, 1], [1, 2, 3]),
    ([5, 1, 5, 3], [1, 3, 5, 5]),
    ([10, -1, 2, 0], [-1, 0, 2, 10]),
])
def test_merge_sort(input_list, expected):
    assert merge_sort(input_list) == expected

@pytest.mark.parametrize("left,right,expected", [
    ([], [], []),
    ([1], [], [1]),
    ([], [2], [2]),
    ([1, 3], [2, 4], [1, 2, 3, 4]),
    ([1, 2], [3, 4, 5], [1, 2, 3, 4, 5]),
    ([5, 6], [1, 2], [1, 2, 5, 6]),
])
def test_merge(left, right, expected):
    assert merge(left, right) == expected
