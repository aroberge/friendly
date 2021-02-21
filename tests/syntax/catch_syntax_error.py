import sys

import pytest

import friendly_traceback
from syntax_errors_descriptions import descriptions


if sys.version_info < (3, 8):
    descriptions["raise_syntax_error_walrus"]["cause"] = "walrus operator"
    descriptions["raise_syntax_error55"]["cause"] = "walrus operator"
if sys.version_info >= (3, 9):
    descriptions["raise_syntax_error66"]["cause"] = "expected an indented block"

friendly_traceback.set_lang("en")


@pytest.mark.parametrize("filename", descriptions.keys())
def test_syntax_errors(filename):
    cause = descriptions[filename]["cause"]

    try:
        exec("from . import %s" % filename)
    except Exception:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()

    if "tab_error" in filename:
        assert "TabError" in result, "TabError identified incorrectly; %s" % filename
    elif "indentation" in filename or "indented" in cause:
        assert "IndentationError" in result, (
            "IndentationError identified incorrectly; %s" % filename
        )
    else:
        assert "SyntaxError" in result, (
            "SyntaxError identified incorrectly; %s" % filename
        )

    unwrapped_result = " ".join(result.split())
    assert cause in unwrapped_result, "\nExpected to see: %s\nIn: %s" % (cause, result)
    if "other causes" in descriptions[filename]:
        other_causes = descriptions[filename]["other causes"]
        for cause in other_causes:
            assert cause in unwrapped_result, "\nExpected to see: %s\nIn: %s" % (
                cause,
                result,
            )
