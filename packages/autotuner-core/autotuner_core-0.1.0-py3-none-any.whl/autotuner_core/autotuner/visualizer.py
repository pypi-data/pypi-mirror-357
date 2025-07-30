import os
import sys
import matplotlib.pyplot as plt
import mplcyberpunk
import networkx as nx
import pandas as pd
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
plt.style.use("cyberpunk")


def plot_runtime_vs_size(csv_path="logs/sort_logs.csv"):
    if not os.path.exists(csv_path):
        print(" No log file found. Run the demo first.")
        return
    df = pd.read_csv(csv_path)
    print("Columns:", df.columns.tolist())
    if "size" not in df.columns or "time_ms" not in df.columns:
        print(" CSV missing required columns.")
        return
    plt.figure(figsize=(10, 6), facecolor="#0f0f0f")
    sns.scatterplot(
        data=df,
        x="size",
        y="time_ms",
        hue="algorithm",
        style="algorithm",
        s=120,
        edgecolor="white",
    )
    plt.title(" Runtime vs Input Size", fontsize=14, color="white")
    plt.xlabel("Input Size", color="white")
    plt.ylabel("Time (ms)", color="white")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.xticks(color="white")
    plt.yticks(color="white")
    mplcyberpunk.add_glow_effects()
    plt.tight_layout()
    plt.show()


def plot_algorithm_distribution(csv_path="logs/sort_logs.csv"):
    df = pd.read_csv(csv_path)
    plt.figure(figsize=(6, 6), facecolor="#0f0f0f")
    sns.countplot(data=df, x="algorithm", palette="pastel")
    plt.title(" Algorithm Selection Count", fontsize=14, color="white")
    plt.xlabel("Algorithm", color="white")
    plt.ylabel("Number of Runs", color="white")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.xticks(color="white")
    plt.yticks(color="white")
    mplcyberpunk.add_glow_effects()
    plt.tight_layout()
    plt.show()


def plot_graph_runtime_vs_nodes(csv_path="logs/graph_logs.csv"):
    if not os.path.exists(csv_path):
        print("No graph log file found!!.")
        return
    df = pd.read_csv(csv_path)
    print("Columns:", df.columns.tolist())
    if "nodes" not in df.columns or "time_ms" not in df.columns:
        print("CSV missing required columns!!.")
        return
    plt.figure(figsize=(10, 6), facecolor="#0f0f0f")
    sns.scatterplot(
        data=df,
        x="nodes",
        y="time_ms",
        hue="algorithm",
        style="algorithm",
        s=120,
        edgecolor="white",
    )
    plt.title(" Graph Runtime vs Node Count", fontsize=14, color="white")
    plt.xlabel("Number of Nodes", color="white")
    plt.ylabel("Time (ms)", color="white")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.xticks(color="white")
    plt.yticks(color="white")
    mplcyberpunk.add_glow_effects()
    plt.tight_layout()
    plt.show()


def plot_graph_algo_distribution(csv_path="logs/graph_logs.csv"):
    df = pd.read_csv(csv_path)
    plt.figure(figsize=(6, 6), facecolor="#0f0f0f")
    sns.countplot(data=df, x="algorithm", palette="Set2")
    plt.title("Graph Algorithm Usage Count", fontsize=14, color="white")
    plt.xlabel("Algorithm", color="white")
    plt.ylabel("Count", color="white")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.xticks(color="white")
    plt.yticks(color="white")
    mplcyberpunk.add_glow_effects()
    plt.tight_layout()
    plt.show()


def visualize_graph(adj_list, title="Graph Visualization"):
    G = nx.Graph()
    is_weighted = any(
        isinstance(neighbors[0], tuple) for neighbors in adj_list.values() if neighbors
    )
    for node, neighbors in adj_list.items():
        for neighbor in neighbors:
            if is_weighted:
                G.add_edge(node, neighbor[0], weight=neighbor[1])
            else:
                G.add_edge(node, neighbor)
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("#000000")
    ax.set_facecolor("#000000")
    pos = nx.spring_layout(G, seed=42)
    edge_labels = nx.get_edge_attributes(G, "weight") if is_weighted else None
    nx.draw(
        G,
        pos,
        with_labels=True,
        ax=ax,
        node_color="#00F0FF",
        edge_color="yellow",
        font_color="red",
        node_size=1000,
        font_size=12,
        linewidths=1.5,
    )
    if edge_labels:
        nx.draw_networkx_edge_labels(
            G,
            pos,
            edge_labels=edge_labels,
            font_color="white",
            font_size=10,
            label_pos=0.5,
            rotate=False,
            bbox=dict(facecolor="#000000", edgecolor="none", boxstyle="round,pad=0.1"),
        )
    ax.set_facecolor("#191818")
    fig.patch.set_facecolor("#211F1F")
    ax.set_title(title, color="white")
    plt.axis("off")
    mplcyberpunk.add_glow_effects()
    plt.tight_layout()
    plt.show()
