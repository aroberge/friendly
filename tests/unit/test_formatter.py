"""Tests of custom formatter.
"""

import subprocess

def run(lang):
    proc = subprocess.run(
        [
            "python",
            "-m",
            "friendly_traceback",
            "--formatter",
            "tests.fake_formatter.get_cause",
            "tests/name_error.py",
            "--lang",
            lang,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    return proc.stderr


def test_formatter_en():
    result = run('en')
    assert "The similar name `pi` was found in the local scope." in result


def test_formatter_fr():
    result = run('fr')
    assert "Le nom semblable `pi` a été trouvé dans la portée locale." in result
