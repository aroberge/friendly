import friendly


def multiple_choices():
    try:
        from math import bsin
    except ImportError:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    assert "ImportError: cannot import name 'bsin'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean one of the following: `sin" in result


def no_suggestion():
    try:
        from math import alphabet_alphabet
    except ImportError:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    assert "ImportError: cannot import name 'alphabet_alphabet'" in result
    if friendly.get_lang() == "en":
        assert "could not be imported is `alphabet_alphabet`" in result


def multiple_import_on_same_line():
    try:
        import circular_a, circular_b
    except ImportError:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    assert "cannot import name 'a'" in result
    if friendly.get_lang() == "en":
        assert "likely caused by what is known as a 'circular import'." in result



def test_Simple_import_error():
    multiple_choices()  # do not record in documentation
    no_suggestion()
    multiple_import_on_same_line()

    try:
        from math import Pi
    except ImportError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ImportError: cannot import name 'Pi'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `pi`" in result
    return result, message


def test_Circular_import():
    try:
        import circular_a
    except ImportError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    # The actual message varies a lot depending on Python version.

    if friendly.get_lang() == "en":
        assert "what is known as a 'circular import'" in result

    return result, message


if __name__ == "__main__":
    print(test_Simple_import_error()[0])
