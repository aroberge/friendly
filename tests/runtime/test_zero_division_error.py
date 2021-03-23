import friendly


def test_Division_operator():
    zero = 0
    try:
        1 / zero
    except ZeroDivisionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ZeroDivisionError: division by zero" in result
    if friendly.get_lang() == "en":
        assert "You are dividing by the following term" in result
    return result, message


def test_Integer_division_operator():
    zero = 0
    try:
        1 // zero
    except ZeroDivisionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "ZeroDivisionError: integer division or modulo by zero" in result
    if friendly.get_lang() == "en":
        assert "You are dividing by the following term" in result
    return result, message


def test_Modulo_operator():
    zero = 0
    try:
        1 % zero
    except ZeroDivisionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ZeroDivisionError: integer division or modulo by zero" in result
    if friendly.get_lang() == "en":
        assert "Using the modulo operator" in result
    return result, message


def test_Divmod():
    zero = 0
    try:
        divmod(1, zero)
    except ZeroDivisionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "ZeroDivisionError: integer division or modulo by zero" in result
    if friendly.get_lang() == "en":
        assert "The second argument of the `divmod()`" in result
    return result, message


def test_Float_modulo():
    zero = 0.
    try:
        1 % zero
    except ZeroDivisionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "ZeroDivisionError: float modulo" in result
    if friendly.get_lang() == "en":
        assert "Using the modulo operator" in result
    return result, message


def test_Float_division():
    zero = 0.
    try:
        1 / zero
    except ZeroDivisionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "ZeroDivisionError: float division by zero" in result
    if friendly.get_lang() == "en":
        assert "You are dividing by the following term" in result
    return result, message


def test_Complex_division():
    zero = 0j
    try:
        1 / zero
    except ZeroDivisionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "ZeroDivisionError: complex division by zero" in result
    if friendly.get_lang() == "en":
        assert "You are dividing by the following term" in result
    return result, message


def test_Raise_zero_negative_power():
    zero = 0
    try:
        zero ** -1
    except ZeroDivisionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "cannot be raised to a negative power" in result
    if friendly.get_lang() == "en":
        assert "You are attempting to raise the number 0 to a negative power" in result
    return result, message


if __name__ == "__main__":
    print(test_Division_operator()[0])

