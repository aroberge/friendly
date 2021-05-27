import math

import friendly

from friendly import console_helpers as helpers

#  ====Important: ensure that we have a clean history after each test.

def empty_history():
    friendly.set_stream(redirect="capture")
    nothing = "Nothing to show: no exception recorded."
    helpers.history()
    return nothing in friendly.get_output()


_hint = "Did you mean `pi`?"
_message = "AttributeError: module"
_what = "An `AttributeError` occurs"
_where = "Exception raised on line"
_why = "Perhaps you meant to write"


def test_back():
    assert empty_history()
    nothing = "Nothing to go back to: no exception recorded."
    helpers.back()
    assert nothing in friendly.get_output()
    try:
        a
    except NameError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.back()
    assert nothing not in friendly.get_output()
    helpers.back()
    assert nothing in friendly.get_output()
    assert empty_history()


def test_friendly_tb():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.friendly_tb()
    result = friendly.get_output()
    assert _hint in result
    assert _message in result
    assert "File" in result
    helpers.back()
    assert empty_history()


def test_hint():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.hint()
    result = friendly.get_output()
    assert _hint in result
    assert _message not in result
    assert "File" not in result
    helpers.back()
    assert empty_history()


def test_history():
    assert empty_history()
    try:
        a
    except NameError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.history()
    assert "NameError" in friendly.get_output()
    helpers.back()
    helpers.history()
    assert empty_history()


def test_more():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.more()
    result = friendly.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where in result
    assert _why in result
    helpers.back()
    assert empty_history()


def test_python_tb():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.python_tb()
    result = friendly.get_output()
    assert "Did you mean `pi`" not in result
    assert "AttributeError" in result
    assert "File" in result
    helpers.back()
    assert empty_history()


def test_what():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.what()
    result = friendly.get_output()
    assert _hint not in result
    assert _message in result
    assert "File" not in result
    assert _what in result
    assert _where not in result
    assert _why not in result
    helpers.back()
    assert empty_history()


def test_what_name():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.what('NameError')
    result = friendly.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where not in result
    assert _why not in result
    assert "NameError" in result
    helpers.back()
    assert empty_history()


def test_what_type():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.what(LookupError)
    result = friendly.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where not in result
    assert _why not in result
    assert "LookupError" in result
    helpers.back()
    assert empty_history()

def test_where():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.where()
    result = friendly.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where in result
    assert _why not in result
    helpers.back()
    assert empty_history()


def test_why():
    assert empty_history()
    try:
        math.Pi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.why()
    result = friendly.get_output()
    assert _hint not in result
    assert _message not in result
    assert "File" not in result
    assert _what not in result
    assert _where not in result
    assert _why in result
    helpers.back()
    assert empty_history()


# The following are processed in formatters.py

def test_why_no_hint():
    assert empty_history()
    try:
        math.PiPiPi
    except AttributeError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.why()
    result = friendly.get_output()
    assert "Python tells us" in result
    helpers.hint()
    result = friendly.get_output()
    assert "I have no suggestion to offer; try `why()`." in result
    helpers.back()
    assert empty_history()

def test_no_why():
    assert empty_history()
    try:
        raise ArithmeticError
    except ArithmeticError:
        friendly.explain_traceback(redirect="capture")
        friendly.get_output()
    helpers.why()
    result = friendly.get_output()
    assert "I have no suggestion to offer." in result
    helpers.hint()
    new_result = friendly.get_output()
    assert "I have no suggestion to offer." in new_result
    helpers.back()
    assert empty_history()