import pytest
from autotuner_core.algorithms.sorting.timsort import timsort

@pytest.mark.parametrize("input_list,expected", [
    ([], []),
    ([1], [1]),
    ([3, 2, 1], [1, 2, 3]),
    ([1, 2, 3], [1, 2, 3]),
    ([5, 1, 5, 3], [1, 3, 5, 5]),
    ([0, -1, -5, 7], [-5, -1, 0, 7]),
])
def test_timsort(input_list, expected):
    assert timsort(input_list) == expected
