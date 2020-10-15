import friendly_traceback


def test_type_error1():
    try:
        a = "a"
        one = 1
        result = a + one
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    py37 = "TypeError: can only concatenate" in result
    py36 = "must be str, not int" in result
    assert py37 or py36
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and an integer (`int`)" in result
    return result, message


def test_type_error1a():
    try:
        a = "a"
        a_list = [1, 2, 3]
        result = a + a_list
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    py37 = "TypeError: can only concatenate" in result
    py36 = "must be str, not list" in result
    assert py37 or py36
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and a `list`" in result
    return result, message


def test_type_error1b():
    try:
        a_tuple = (1, 2, 3)
        a_list = [1, 2, 3]
        result = a_tuple + a_list
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: can only concatenate" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `tuple` and a `list`" in result
    return result, message


def test_type_error2():
    try:
        one = 1
        none = None
        result = one + none
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for +:" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "an integer (`int`) and a variable equal to `None` (`NoneType`)" in result
        )
    return result, message


def test_type_error2a():
    try:
        one = 1
        two = "two"
        one += two
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for +=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a string (`str`)" in result
    return result, message


def test_type_error3():
    try:
        a = (1, 2)
        b = [3, 4]
        result = a - b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for -:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `tuple` and a `list`" in result
    return result, message


def test_type_error3a():
    try:
        a = (1, 2)
        b = [3, 4]
        b -= a
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for -=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `list` and a `tuple`" in result
    return result, message


def test_type_error4():
    try:
        a = 1j
        b = {2, 3}
        result = a * b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for *:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a complex number and a `set`" in result
    return result, message


def test_type_error4a():
    try:
        a = 1j
        b = {2, 3}
        b *= a
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for *=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `set` and a complex number" in result
    return result, message


def test_type_error5():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a / b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for /:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a dictionary (`dict`) and a number (`float`)" in result
    return result, message


def test_type_error5a():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        b /= a
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for /=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a number (`float`) and a dictionary (`dict`)" in result
    return result, message


def test_type_error5b():
    try:
        a = {1: 1, 2: 2}
        b = 1
        result = a // b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for //:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a dictionary (`dict`) and an integer (`int`)" in result
    return result, message


def test_type_error5c():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        b //= a
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for //=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a dictionary (`dict`)"
    return result, message


def test_type_error6():
    try:
        a = "a"
        b = 2
        result = a & b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for &:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and an integer (`int`)" in result
    return result, message


def test_type_error6a():
    try:
        a = "a"
        b = 2
        b &= a
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for &=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a string (`str`)" in result
    return result, message


def test_type_error7():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a ** b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for ** or pow():" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to exponentiate (raise to a power)" in result
    return result, message


def test_type_error7a():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        a **= b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for ** or pow():" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to exponentiate (raise to a power)" in result
    return result, message


def test_type_error8():
    try:
        a = "a"
        b = 42
        result = a >> b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for >>:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to perform the bit shifting operation >>" in result
    return result, message


def test_type_error8a():
    try:
        a = "a"
        b = 42
        a >>= b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for >>=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to perform the bit shifting operation >>" in result
    return result, message


def test_type_error9():
    try:
        a = "a"
        b = 2
        result = a @ b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for @:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the operator @" in result
    return result, message


def test_type_error9a():
    try:
        a = "a"
        b = 2
        a @= b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for @=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the operator @" in result
    return result, message


def test_type_error10():
    try:
        a = "a"
        b = 42
        b < a
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: '<' not supported between instances of 'int' and 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to do an order comparison (<)" in result
    return result, message


def test_type_error11():
    try:
        a = +"abc"
        print(a)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: bad operand type for unary +: 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '+'" in result
    return result, message


def test_type_error11a():
    try:
        a = -[1, 2, 3]
        print(a)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: bad operand type for unary -: 'list'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '-'" in result
    return result, message


def test_type_error11b():
    try:
        a = ~(1, 2, 3)
        print(a)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: bad operand type for unary ~: 'tuple'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '~'" in result
    return result, message


def test_type_error12():
    a = (1, 2, 3)
    try:
        a[0] = 0
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'tuple' object does not support item assignment" in result
    if friendly_traceback.get_lang() == "en":
        assert "In Python, some objects are known as immutable:" in result
    return result, message


def test_type_error13():
    def fn(*, b=1):
        pass

    try:
        fn(1)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError" in result
    assert "fn() takes 0 positional arguments but 1 was given" in result
    if friendly_traceback.get_lang() == "en":
        assert "1 positional argument(s) while it requires 0" in result
    return result, message


def test_type_error13a():
    class A:
        def f(x):
            pass

    try:
        A().f(1)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError" in result
    assert "f() takes 1 positional argument but 2 were given" in result
    if friendly_traceback.get_lang() == "en":
        assert "2 positional argument(s) while it requires 1" in result
        assert "Perhaps you forgot `self`" in result
    return result, message


def test_type_error14():
    def fn(a, b, c):
        pass

    try:
        fn(1)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError" in result
    assert "fn() missing 2 required positional argument" in result
    if friendly_traceback.get_lang() == "en":
        assert "fewer positional arguments than it requires (2 missing)." in result
    return result, message


def test_type_error15():
    try:
        _ = (1, 2)(3, 4)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'tuple' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "I suspect that you had an object of this type, a `tuple`," in result
    return result, message


def test_type_error15a():
    try:
        _ = [1, 2](3, 4)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'list' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "I suspect that you had an object of this type, a `list`," in result
    return result, message


def test_type_error16():
    try:
        raise "exception"
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: exceptions must derive from BaseException" in result
    if friendly_traceback.get_lang() == "en":
        assert "In Python 3, exceptions must be derived from BaseException." in result
    return result, message


def test_type_error17():
    try:
        "a" * "2"
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "Perhaps you forgot to convert a string into an integer using `int()`."
            in result
        )


if __name__ == "__main__":
    print(test_type_error1a()[0])
