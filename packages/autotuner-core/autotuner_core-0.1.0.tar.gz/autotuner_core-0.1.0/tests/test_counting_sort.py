import pytest
from autotuner_core.algorithms.sorting.counting_sort import counting_sort
@pytest.mark.parametrize("input_list,expected", [
    ([], []),                          
    ([1], [1]),                        
    ([3, 1, 2], [1, 2, 3]),           
    ([1, 2, 3], [1, 2, 3]),            
    ([5, 1, 5, 3], [1, 3, 5, 5]),      
    ([0, -1, -2], [-2, -1, 0]),        
    ([100, 99, 101], [99, 100, 101]),  
])
def test_counting_sort_valid(input_list, expected):
    assert counting_sort(input_list) == expected
def test_counting_sort_invalid_type():
    with pytest.raises(ValueError, match="Counting sort only supports integer values."):
        counting_sort([1, "a", 3.5])
