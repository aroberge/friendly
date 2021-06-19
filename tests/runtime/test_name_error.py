import pydoc
import tkinter

import friendly
from math import *

def test_Generic():
    try:
        this = something
    except NameError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'something' is not defined" in result
    if friendly.get_lang() == "en":
        assert "In your program, no object with the name `something` exists." in result
    return result, message

x: 3

def test_Annotated_variable():
    try:
        y = x
    except NameError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'x' is not defined" in result
    if friendly.get_lang() == "en":
        assert "x = 3" in result
    return result, message

alphabet = 'abc'


def test_Synonym():
    try:
        a = i
    except NameError:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'i' is not defined" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `1j`" in result

    try:
        a = j
    except NameError:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'j' is not defined" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `1j`" in result

    nabs = 1
    try:
        x = babs(-1)
    except NameError as e:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'babs' is not defined" in result
    if friendly.get_lang() == "en":
        assert "perhaps you meant one of the following" in result

    try:
        alphabets
    except NameError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    if friendly.get_lang() == "en":
        assert "The similar name `alphabet` was found in the global scope" in result

    try:
        char
    except NameError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    if friendly.get_lang() == "en":
        assert "The Python builtin `chr` has a similar name." in result

    try:
        cost  # wrote from math import * above
    except NameError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "NameError: name 'cost' is not defined" in result
    if friendly.get_lang() == "en":
        assert "perhaps you meant one of the following" in result
    return result, message


def test_Missing_import():
    try:
        unicodedata.something
    except NameError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "NameError: name 'unicodedata' is not defined" in result
    if friendly.get_lang() == "en":
        assert "Perhaps you forgot to import `unicodedata`" in result
    return result, message


def test_Free_variable_referenced():
    def outer():
        def inner():
            return var
        inner()
        var = 4

    try:
        outer()
    except NameError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "free variable 'var' referenced" in result
    if friendly.get_lang() == "en":
        assert "that exists in an enclosing scope" in result
        assert "but has not yet been assigned a value." in result
    return result, message

if __name__ == "__main__":
    print(test_Generic()[0])
