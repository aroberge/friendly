"""In this file, we test to ensure the traceback is properly trimmed
of all ignored files.
"""

import friendly as ft


def test_uncleaned_traceback():
    """Assert this test filename appear in tracebacks if we don't exclude
    it.
    """
    ft.install(redirect="capture")

    try:
        from . import raise_exception
    except ValueError:
        ft.explain_traceback()

    output = ft.get_output()
    assert "test_clean_traceback" in output
    assert "André" in output

    # cleanup for other tests
    ft.uninstall()


def test_cleaned_traceback():
    """Assert this test filename does not appear in tracebacks if we
    exclude it.
    """
    ft.install(redirect="capture")
    ft.exclude_file_from_traceback(__file__)

    try:
        from . import raise_exception
    except ValueError:
        ft.explain_traceback()

    output = ft.get_output()
    assert "test_clean_traceback" not in output
    assert "André" in output

    # cleanup for other tests
    ft.path_info.include_file_in_traceback(__file__)
    ft.uninstall()
