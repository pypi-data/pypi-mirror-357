from autotuner_core.algorithms.graphs.dijkstra_matrix import dijkstra_matrix

def test_dijkstra_matrix_basic():
    matrix = [
        [0, 2, 4, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 5],
        [0, 0, 0, 0]
    ]
    assert dijkstra_matrix(matrix, 0) == [0, 2, 3, 8]

def test_dijkstra_matrix_unweighted():
    matrix = [
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
    ]
    result = dijkstra_matrix(matrix, 0)
    assert result == [0, 1, 1, 2]
    
def test_dijkstra_matrix_disconnected():
    matrix = [
        [0, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0]
    ]
    assert dijkstra_matrix(matrix, 0) == [0, 1, float("inf"), float("inf")]
