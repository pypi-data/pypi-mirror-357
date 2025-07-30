import subprocess
import sys
import os
import pytest

SCRIPT_PATH = os.path.join("autotuner_core", "cli", "sort_cli.py")

@pytest.mark.parametrize("args", [
    ["1", "5", "3"],                                      
    ["1", "5", "3", "--algo", "merge"],                   
    ["1", "5", "3", "--algo", "all_algorithms"],         
])
def test_sorting_cli_success(args):
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH] + args,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Sorted Array" in result.stdout

def test_sorting_cli_invalid_algo():
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, "1", "2", "3", "--algo", "invalid_algo"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "invalid choice" in result.stderr.lower()
