import friendly_traceback


def test_Can_only_concatenate():
    try:
        a = "a"
        one = 1
        result = a + one
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    py37 = "TypeError: can only concatenate" in result
    py36 = "must be str, not int" in result
    assert py37 or py36
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and an integer (`int`)" in result

    try:
        a = "a"
        a_list = [1, 2, 3]
        result = a + a_list
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    py37 = "TypeError: can only concatenate" in result
    py36 = "must be str, not list" in result
    assert py37 or py36
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and a `list`" in result

    try:
        a_tuple = (1, 2, 3)
        a_list = [1, 2, 3]
        result = a_tuple + a_list
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: can only concatenate" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `tuple` and a `list`" in result
    return result, message


def test_Unsupported_operand_types():
    try:
        one = 1
        none = None
        result = one + none
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for +:" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "an integer (`int`) and a variable equal to `None` (`NoneType`)" in result
        )

    try:
        one = 1
        two = "two"
        one += two
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for +=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a string (`str`)" in result

    try:
        a = (1, 2)
        b = [3, 4]
        result = a - b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for -:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `tuple` and a `list`" in result

    try:
        a = (1, 2)
        b = [3, 4]
        b -= a
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for -=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `list` and a `tuple`" in result

    try:
        a = 1j
        b = {2, 3}
        result = a * b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for *:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a complex number and a `set`" in result

    try:
        a = 1j
        b = {2, 3}
        b *= a
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for *=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a `set` and a complex number" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a / b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for /:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a dictionary (`dict`) and a number (`float`)" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        b /= a
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for /=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a number (`float`) and a dictionary (`dict`)" in result

    try:
        a = {1: 1, 2: 2}
        b = 1
        result = a // b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for //:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a dictionary (`dict`) and an integer (`int`)" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        b //= a
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for //=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a dictionary (`dict`)"

    try:
        a = "a"
        b = 2
        result = a & b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for &:" in result
    if friendly_traceback.get_lang() == "en":
        assert "a string (`str`) and an integer (`int`)" in result

    try:
        a = "a"
        b = 2
        b &= a
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for &=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "an integer (`int`) and a string (`str`)" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a ** b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for ** or pow():" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to exponentiate (raise to a power)" in result

    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        a **= b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for ** or pow():" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to exponentiate (raise to a power)" in result

    try:
        a = 3.0
        b = 42
        result = a ^ b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for ^:" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `a ** b`" in result

    try:
        a = 3.0
        b = 42
        a ^= b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for ^=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `a **= b`" in result

    try:
        a = "a"
        b = 42
        result = a >> b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for >>:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to perform the bit shifting operation >>" in result

    try:
        a = "a"
        b = 42
        a >>= b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for >>=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to perform the bit shifting operation >>" in result

    try:
        a = "a"
        b = 2
        result = a @ b
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for @:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the operator @" in result

    try:
        a = "a"
        b = 2
        a @= b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: unsupported operand type(s) for @=:" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the operator @" in result
    return result, message


def test_Comparison_not_supported():
    try:
        a = "a"
        b = 42
        b < a
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: '<' not supported between instances of 'int' and 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to do an order comparison (<)" in result
    return result, message


def test_Bad_type_for_unary_operator():
    try:
        a = +"abc"
        print(a)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: bad operand type for unary +: 'str'" in result
    assert not "+=" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '+'" in result

    try:
        a = -[1, 2, 3]
        print(a)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: bad operand type for unary -: 'list'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '-'" in result

    try:
        a = ~(1, 2, 3)
        print(a)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: bad operand type for unary ~: 'tuple'" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '~'" in result

    try:
        # fmt: off
        a = "abc"
        a =+ "def"
        # fmt: on
        print(a)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: bad operand type for unary +: 'str'" in result
    assert "Perhaps you meant to write `+=`" in result
    if friendly_traceback.get_lang() == "en":
        assert "You tried to use the unary operator '+'" in result
    return result, message


def test_Tuple_no_item_assignment():
    a = (1, 2, 3)
    try:
        a[0] = 0
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: 'tuple' object does not support item assignment" in result
    if friendly_traceback.get_lang() == "en":
        assert "In Python, some objects are known as immutable:" in result
        assert "Perhaps you meant to use a list" in result
    return result, message


def test_Too_many_positional_argument():
    def fn(*, b=1):
        pass

    try:
        fn(1)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError" in result
    assert "fn() takes 0 positional arguments but 1 was given" in result
    if friendly_traceback.get_lang() == "en":
        assert "1 positional argument(s) while it requires 0" in result

    class A:
        def f(x):
            pass

    try:
        A().f(1)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError" in result
    assert "f() takes 1 positional argument but 2 were given" in result
    if friendly_traceback.get_lang() == "en":
        assert "2 positional argument(s) while it requires 1" in result
        # assert "Perhaps you forgot `self`" in result
    return result, message


def test_Too_few_positional_argument():
    def fn(a, b, c):
        pass

    try:
        fn(1)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError" in result
    assert "fn() missing 2 required positional argument" in result
    if friendly_traceback.get_lang() == "en":
        assert "fewer positional arguments than it requires (2 missing)." in result
    return result, message


def test_Not_callable():
    try:
        _ = (1, 2)(3, 4)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: 'tuple' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "you have a missing comma between the object" in result

    try:
        _ = 3(4 + 4)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: 'int' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot a multiplication operator" in result

    try:
        _ = [1, 2](3, 4)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'list' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "you have a missing comma between the object" in result

    # Test with dotted name
    class A:
        a_list = [1, 2, 3]
    try:
        b = A()
        b.a_list(3)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'list' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "b.a_list[3]" in result

    try:
        _ = [1, 2](3 + 4)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'list' object is not callable" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you meant to use `[]` instead of `()`" in result
    return result, message


def test_Derive_from_BaseException():
    try:
        raise "exception"
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: exceptions must derive from BaseException" in result
    if friendly_traceback.get_lang() == "en":
        assert "In Python 3, exceptions must be derived from BaseException." in result
    return result, message


def test_Cannot_multiply_by_non_int():

    try:
        "b" * "a"
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            'You can only multiply sequences, such as'
            in result
        )

    try:
        "3" * "a"
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            'Did you forget to convert `"3"` into an integer?'
            in result
        )

    a = b = c = "2"
    try:
        d = a * b * c
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            'Did you forget to convert `a` and `b` into integers?'
            in result
        )

    a = "abc"
    try:
        a *= c
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            'Did you forget to convert `c` into an integer?'
            in result
        )

    try:
        "a" * "2"
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: can't multiply sequence by non-int of type 'str'" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            'Did you forget to convert `"2"` into an integer?'
            in result
        )
    return result, message


def test_Not_an_integer():
    try:
        range([1, 2])
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: 'list' object cannot be interpreted as an integer" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to convert " not in result

    try:
        range("2")
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: 'str' object cannot be interpreted as an integer" in result
    if friendly_traceback.get_lang() == "en":
        assert 'Perhaps you forgot to convert `"2"` into an integer.' in result

    try:
        range(1.0)
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: 'float' object cannot be interpreted as an integer" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to convert `1.0" in result

    c, d = "2", "3"
    try:
        range(c, d)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: 'str' object cannot be interpreted as an integer" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to convert `c, d` into integers." in result
    return result, message


def test_Indices_must_be_integers_or_slices():
    a = [1, 2, 3]

    try:
        a[1, 2]
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: list indices must be integers or slices" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `a[1: 2]`" in result

    a = (1, 2, 3)
    try:
        a[2.0]
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: tuple indices must be integers or slices" in result
    if friendly_traceback.get_lang() == "en":
        assert "Perhaps you forgot to convert `2.0` into an integer." in result

    try:
        [1, 2, 3]["2"]
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "TypeError: list indices must be integers or slices" in result
    if friendly_traceback.get_lang() == "en":
        assert 'Perhaps you forgot to convert `"2"` into an integer.' in result
    return result, message


if __name__ == "__main__":
    print(test_Not_an_integer()[0])
