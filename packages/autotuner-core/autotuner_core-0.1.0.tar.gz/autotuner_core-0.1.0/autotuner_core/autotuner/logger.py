import csv
import os
from datetime import datetime

LOG_FILE = "logs/sort_logs.csv"


def init_logger(log_path="logs/sort_logs.csv"):
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(log_path) or os.stat(log_path).st_size == 0:
        with open(log_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["timestamp", "algorithm", "size", "sortedness_score", "time_ms"]
            )


def log_run(algorithm, features, time_ms):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                timestamp,
                algorithm,
                features["size"],
                features["sortedness_score"],
                time_ms,
            ]
        )


GRAPH_LOG_FILE = "logs/graph_logs.csv"


def init_graph_logger():
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.exists(GRAPH_LOG_FILE)
    with open(GRAPH_LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists or os.stat(GRAPH_LOG_FILE).st_size == 0:
            writer.writerow(
                ["timestamp", "algorithm", "nodes", "edges", "avg_degree", "time_ms"]
            )


def log_graph_run(algorithm, features, time_ms):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(GRAPH_LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                timestamp,
                algorithm,
                features["num_nodes"],
                features["num_edges"],
                features["avg_degree"],
                time_ms,
            ]
        )
