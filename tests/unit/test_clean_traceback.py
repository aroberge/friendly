"""In this file, we test to ensure the traceback is properly trimmed
of all ignored files.
"""

import friendly


def test_uncleaned_traceback():
    """Assert this test filename appear in tracebacks if we don't exclude
    it.
    """
    friendly.install(redirect="capture")
    old_debug = friendly.debug_helper.DEBUG
    friendly.debug_helper.DEBUG = False

    try:
        from . import raise_exception
    except ValueError:
        friendly.explain_traceback()

    output = friendly.get_output()
    assert "test_clean_traceback" in output
    assert "André" in output

    # cleanup for other tests
    friendly.uninstall()
    friendly.debug_helper.DEBUG = old_debug


def test_cleaned_traceback():
    """Assert this test filename does not appear in tracebacks if we
    exclude it.
    """
    friendly.install(redirect="capture")
    friendly.exclude_file_from_traceback(__file__)
    old_debug = friendly.debug_helper.DEBUG
    friendly.debug_helper.DEBUG = False

    try:
        from . import raise_exception
    except ValueError:
        friendly.explain_traceback()

    output = friendly.get_output()
    assert "test_clean_traceback" not in output
    assert "André" in output

    # cleanup for other tests
    friendly.path_info.include_file_in_traceback(__file__)
    friendly.uninstall()
    friendly.debug_helper.DEBUG = old_debug
