"""Tests of custom formatter.
"""

import subprocess
import sys


def run(lang):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "friendly",
            "--formatter",
            "tests.fake_formatter.get_cause",
            "tests/name_error.py",
            "--lang",
            lang,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
    )
    return proc.stderr


def test_formatter_en():
    result = run('en')
    assert "The similar name `pi` was found in the local scope." in result


def test_formatter_fr():
    result = run('fr')
    assert "Le nom semblable `pi` a été trouvé dans la portée locale." in result
