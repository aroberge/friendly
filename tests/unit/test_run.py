"""Tests for run(), used as a program launcher from an editor
"""

from io import StringIO
import friendly_traceback
from contextlib import redirect_stdout

def test_run_error_en():
    friendly_traceback.run(
        "../name_error.py",
        include="explain",  # comprehensive
        console=False,
        redirect="capture",
    )
    result = friendly_traceback.get_output()
    friendly_traceback.uninstall()
    assert "The similar name `pi` was found in the local scope." in result


def test_run_error_fr():
    friendly_traceback.run(
        "../name_error.py",
        lang="fr",
        include="why",  # more restricted than the English test
        console=False,
        redirect="capture",
    )
    result = friendly_traceback.get_output()
    friendly_traceback.set_lang('en')
    friendly_traceback.uninstall()
    assert "Le nom semblable `pi` a été trouvé dans la portée locale." in result


def test_run_get_mod_dict():
    """Ensure that we capture the dict of the module that was executed
       with no exception raised.
    """
    file_capture = StringIO()
    with redirect_stdout(file_capture):
        mod_dict = friendly_traceback.run(
            "tests/adder.py",  # run from where pytest is run
            console=False,
            args=("1", "2.5", "3")
        )
    assert "total" in mod_dict
    assert mod_dict["total"] == 6.5
    assert "The sum is 6.5." in file_capture.getvalue()

