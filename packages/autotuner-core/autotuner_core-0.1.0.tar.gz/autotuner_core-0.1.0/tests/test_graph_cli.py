import subprocess
import sys
import os
import json
import pytest

SCRIPT_PATH = os.path.join("autotuner_core", "cli", "graph_cli.py")
VALID_GRAPH_FILE = "temp_test_graph.json"
INVALID_GRAPH_FILE = "nonexistent.json"

def setup_module(module):
    graph = {
        "0": [1, 2],
        "1": [0, 3],
        "2": [0],
        "3": [1]
    }
    with open(VALID_GRAPH_FILE, "w") as f:
        json.dump(graph, f)

def teardown_module(module):
    if os.path.exists(VALID_GRAPH_FILE):
        os.remove(VALID_GRAPH_FILE)

def run_cli(args):
    return subprocess.run(
        [sys.executable, SCRIPT_PATH] + args,
        capture_output=True,
        text=True
    )

def test_demo_mode():
    result = run_cli(["--demo"])
    assert result.returncode == 0
    assert "demo graph" in result.stdout.lower()
    assert "selected algorithm" in result.stdout.lower()

def test_valid_file_input():
    result = run_cli(["--file", VALID_GRAPH_FILE])
    assert result.returncode == 0
    assert "loaded graph" in result.stdout.lower()
    assert "selected algorithm" in result.stdout.lower()

def test_invalid_file_input():
    result = run_cli(["--file", INVALID_GRAPH_FILE])
    assert result.returncode == 0
    assert "error loading graph" in result.stdout.lower()

def test_no_graph_provided():
    result = run_cli([])
    assert result.returncode == 0
    assert "please use --demo or --file" in result.stdout.lower()

def test_all_algorithms_option():
    result = run_cli(["--file", VALID_GRAPH_FILE, "--algo", "all_algorithms"])
    assert result.returncode == 0
    assert "selected algorithm" in result.stdout.lower()
    assert "all algorithm outputs" in result.stdout.lower()