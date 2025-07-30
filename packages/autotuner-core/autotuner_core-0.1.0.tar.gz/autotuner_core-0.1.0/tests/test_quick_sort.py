import pytest
from autotuner_core.algorithms.sorting.quick_sort import quick_sort

@pytest.mark.parametrize("input_list,expected", [
    ([], []),                                
    ([1], [1]),                              
    ([3, 2, 1], [1, 2, 3]),                  
    ([1, 2, 3], [1, 2, 3]),                  
    ([5, 3, 8, 3], [3, 3, 5, 8]),            
    ([0, -1, -5, 7, 3], [-5, -1, 0, 3, 7]),   
    ([1, 2, 2, 1], [1, 1, 2, 2]),           
])
def test_quick_sort(input_list, expected):
    assert quick_sort(input_list) == expected
