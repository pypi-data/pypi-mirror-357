import copy

from autotuner_core.algorithms.graphs.bfs import bfs
from autotuner_core.algorithms.graphs.cycle_detection import has_cycle
from autotuner_core.algorithms.graphs.dfs import dfs
from autotuner_core.algorithms.graphs.dijkstra_heap import dijkstra_heap
from autotuner_core.algorithms.graphs.dijkstra_matrix import dijkstra_matrix
from autotuner_core.algorithms.graphs.toposort import topo_sort
from autotuner_core.algorithms.graphs.union_find import UnionFind
from autotuner_core.autotuner.graph_features import get_graph_features


def choose_graph_algorithm(adj_list, algo="auto"):
    if not adj_list:
        return {
            "algorithm": "empty_graph",
            "features": {"num_nodes": 0, "num_edges": 0},
            "output": [],
        }
    adj_list = copy.deepcopy(adj_list)
    weighted = any(
        isinstance(neighbors[0], (tuple, list)) and len(neighbors[0]) == 2
        for neighbors in adj_list.values()
        if neighbors
    )
    if weighted:
        for u in adj_list:
            for i in range(len(adj_list[u])):
                if isinstance(adj_list[u][i], int):
                    adj_list[u][i] = (adj_list[u][i], 1)
    features = get_graph_features(adj_list)
    num_nodes = features["num_nodes"]
    has_cycle_flag = has_cycle(adj_list)
    if algo == "auto":
        if weighted:
            return {
                "algorithm": "dijkstra_heap",
                "features": features,
                "output": dijkstra_heap(adj_list, 0),
            }
        if not has_cycle_flag:
            return {
                "algorithm": "topological_sort",
                "features": features,
                "output": topo_sort(adj_list, num_nodes),
            }
        if num_nodes <= 10:
            return {
                "algorithm": "dfs",
                "features": features,
                "output": dfs(adj_list, 0),
            }
        return {"algorithm": "bfs", "features": features, "output": bfs(adj_list, 0)}
    elif algo == "bfs":
        return {"algorithm": "bfs", "features": features, "output": bfs(adj_list, 0)}
    elif algo == "dfs":
        return {"algorithm": "dfs", "features": features, "output": dfs(adj_list, 0)}
    elif algo == "cycle_detection":
        return {
            "algorithm": "cycle_detection",
            "features": features,
            "output": has_cycle_flag,
        }
    elif algo == "union_find":
        return {
            "algorithm": "union_find_cycle_check",
            "features": features,
            "output": run_union_cycle_check(adj_list, num_nodes),
        }
    elif algo == "topological_sort":
        return {
            "algorithm": "topological_sort",
            "features": features,
            "output": topo_sort(adj_list, num_nodes),
        }
    elif algo == "dijkstra_matrix":
        if not weighted:
            raise ValueError("Dijkstra requires a weighted graph.")
        return {
            "algorithm": "dijkstra_matrix",
            "features": features,
            "output": dijkstra_matrix(adj_list, 0),
        }
    elif algo == "dijkstra_heap":
        if not weighted:
            raise ValueError("Dijkstra requires a weighted graph.")
        return {
            "algorithm": "dijkstra_heap",
            "features": features,
            "output": dijkstra_heap(adj_list, 0),
        }
    elif algo == "all_algorithms":
        weighted_adj_list = copy.deepcopy(adj_list)
        if weighted:
            for u in weighted_adj_list:
                for i in range(len(weighted_adj_list[u])):
                    if isinstance(weighted_adj_list[u][i], int):
                        weighted_adj_list[u][i] = (weighted_adj_list[u][i], 1)
        result = {
            "algorithm": "all_algorithms",
            "features": features,
            "output": {
                "bfs": bfs(copy.deepcopy(adj_list), 0),
                "dfs": dfs(copy.deepcopy(adj_list), 0),
                "cycle_detected": has_cycle(copy.deepcopy(adj_list)),
                "union_find_cycle": run_union_cycle_check(
                    copy.deepcopy(adj_list), num_nodes
                ),
                "topo_sort": topo_sort(copy.deepcopy(adj_list), num_nodes),
            },
        }
        if weighted:
            result["output"]["dijkstra_heap"] = dijkstra_heap(
                copy.deepcopy(weighted_adj_list), 0
            )
            result["output"]["dijkstra_matrix"] = dijkstra_matrix(
                copy.deepcopy(weighted_adj_list), 0
            )
        return result
    else:
        return {"algorithm": "unknown", "features": features, "output": None}


def run_union_cycle_check(adj_list, n):
    uf = UnionFind(n)
    for u in adj_list:
        for v in adj_list[u]:
            if isinstance(v, (tuple, list)):
                v = v[0]
            if u < v:
                if not uf.union(u, v):
                    return True
    return False
