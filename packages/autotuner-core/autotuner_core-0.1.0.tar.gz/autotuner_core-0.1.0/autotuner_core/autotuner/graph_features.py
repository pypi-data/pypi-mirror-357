def get_graph_features(adj_list):
    num_nodes = len(adj_list)
    num_edges = sum(len(neighbors) for neighbors in adj_list.values()) // 2
    avg_degree = (2 * num_edges) / num_nodes if num_nodes > 0 else 0
    density = (2 * num_edges) / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0
    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "avg_degree": round(avg_degree, 2),
        "density": round(density, 3),
        "is_dense": density > 0.5,
    }
