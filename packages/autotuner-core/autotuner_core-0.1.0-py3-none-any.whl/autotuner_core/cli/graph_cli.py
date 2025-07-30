import argparse
import json
import os

from autotuner_core.autotuner.graph_switcher import choose_graph_algorithm


def convert_graph_data(raw_graph):
    converted = {}
    for u, neighbors in raw_graph.items():
        u = int(u)
        converted_neighbors = []
        for v in neighbors:
            if (
                isinstance(v, list)
                and len(v) == 2
                and all(isinstance(i, (int, float)) for i in v)
            ):
                converted_neighbors.append(tuple(v))
            else:
                converted_neighbors.append(v)
        converted[u] = converted_neighbors
    return converted


def load_graph_from_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Graph file not found: {filepath}")
    with open(filepath, "r") as f:
        raw_graph = json.load(f)
        return convert_graph_data(raw_graph)


def main():
    parser = argparse.ArgumentParser(description="AutoTuner Graph CLI")

    parser.add_argument(
        "--demo", action="store_true", help="Run a demo graph through AutoTuner"
    )
    parser.add_argument(
        "--file", type=str, help="Path to JSON file containing the graph"
    )
    parser.add_argument(
        "--algo",
        type=str,
        choices=[
            "auto",
            "bfs",
            "dfs",
            "cycle_detection",
            "union_find",
            "topological_sort",
            "dijkstra_matrix",
            "dijkstra_heap",
            "all_algorithms",
        ],
        default="auto",
        help="Specify the algorithm to use (default: auto)",
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Visualize the graph using networkx"
    )
    args = parser.parse_args()
    if args.demo:
        graph = {0: [1, 2], 1: [0, 3], 2: [0, 3], 3: [1, 2, 4], 4: [3, 5], 5: [4]}
        print(" Running demo graph...\n")
    elif args.file:
        try:
            graph = load_graph_from_file(args.file)
            print(f" Loaded graph from {args.file}\n")
        except Exception as e:
            print(f" Error loading graph: {e}")
            return
    else:
        print(" Please use --demo or --file to provide a graph.")
        return
    try:
        result = choose_graph_algorithm(graph, algo=args.algo)
        print("\n Graph Features:")
        for k, v in result["features"].items():
            print(f"   {k}: {v}")
        print(f"\n Selected Algorithm: {result['algorithm']}")
        print(f" Output: {result['output']}")
        if result["algorithm"] == "all_algorithms":
            print("\n All Algorithm Outputs:")
            for name, output in result["output"].items():
                print(f"   {name}: {output}")
        if args.visualize:
            try:
                import matplotlib.pyplot as plt
                import networkx as nx

                G = (
                    nx.DiGraph()
                    if result["features"].get("directed", True)
                    else nx.Graph()
                )
                for u in graph:
                    for v in graph[u]:
                        if isinstance(v, tuple):
                            G.add_edge(u, v[0], weight=v[1])
                        else:
                            G.add_edge(u, v)
                pos = nx.spring_layout(G)
                labels = nx.get_edge_attributes(G, "weight")
                nx.draw(
                    G,
                    pos,
                    with_labels=True,
                    node_color="skyblue",
                    edge_color="gray",
                    node_size=1500,
                )
                if labels:
                    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
                plt.title("Graph Visualization")
                plt.show()
            except ImportError:
                print(" Visualization requires networkx ")
                print("and matplotlib. Install them via pip.")
    except Exception as e:
        print(f"\n Error while processing graph: {e}")


if __name__ == "__main__":
    main()
