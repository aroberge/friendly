"""Tests of running a program that uses command line arguments.
"""

import subprocess

def run(*args):
    proc = subprocess.run(
        [
            "venv-friendly3.8/scripts/python",
            "-m",
            "friendly",
            "tests/adder.py",
            "--",
            *args,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    return proc.stdout


def test_args_float():
    result = run("1", "2.5", "3")
    assert "The sum is 6.5." in result


def test_args_to_int():
    result = run("1", "2.5", "3", "--to_int")
    assert "The sum is 6." in result
