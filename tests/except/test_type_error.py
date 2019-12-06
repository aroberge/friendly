import friendly_traceback


def test_type_error1():
    try:
        a = "a"
        one = 1
        result = a + one
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    py37 = "TypeError: can only concatenate" in result
    py36 = "must be str, not int" in result
    assert py37 or py36
    return result


def test_type_error1a():
    try:
        a = "a"
        a_list = [1, 2, 3]
        result = a + a_list
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    py37 = "TypeError: can only concatenate" in result
    py36 = "must be str, not list" in result
    assert py37 or py36
    return result


def test_type_error1b():
    try:
        a_tuple = (1, 2, 3)
        a_list = [1, 2, 3]
        result = a_tuple + a_list
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: can only concatenate" in result
    return result


def test_type_error2():
    try:
        one = 1
        none = None
        result = one + none
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for +:" in result
    return result


def test_type_error2a():
    try:
        one = 1
        two = "two"
        one += two
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for +=:" in result
    return result


def test_type_error3():
    try:
        a = (1, 2)
        b = [3, 4]
        result = a - b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for -:" in result
    return result


def test_type_error3a():
    try:
        a = (1, 2)
        b = [3, 4]
        a -= b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for -=:" in result
    return result


def test_type_error4():
    try:
        a = 1j
        b = {2, 3}
        result = a * b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for *:" in result
    return result


def test_type_error4a():
    try:
        a = 1j
        b = {2, 3}
        a *= b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for *=:" in result
    return result


def test_type_error5():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a / b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for /:" in result
    return result


def test_type_error5a():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        a /= b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for /=:" in result
    return result


def test_type_error5b():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a // b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for //:" in result
    return result


def test_type_error5c():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        a //= b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for //=:" in result
    return result


def test_type_error6():
    try:
        a = "a"
        b = 2
        result = a & b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for &:" in result
    return result


def test_type_error6a():
    try:
        a = "a"
        b = 2
        a &= b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for &=:" in result
    return result


def test_type_error7():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        result = a ** b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for ** or pow():" in result
    return result


def test_type_error7a():
    try:
        a = {1: 1, 2: 2}
        b = 3.1416
        a **= b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for ** or pow():" in result
    return result


def test_type_error8():
    try:
        a = "a"
        b = 42
        result = a >> b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for >>:" in result
    return result


def test_type_error8a():
    try:
        a = "a"
        b = 42
        a >>= b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for >>=:" in result
    return result


def test_type_error9():
    try:
        a = "a"
        b = 2
        result = a @ b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for @:" in result
    return result


def test_type_error9a():
    try:
        a = "a"
        b = 2
        a @= b
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: unsupported operand type(s) for @=:" in result
    return result


def test_type_error10():
    try:
        a = "a"
        b = 42
        b < a
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: '<' not supported between instances of 'int' and 'str'" in result
    return result


def test_type_error11():
    try:
        a = +"abc"
        print(a)
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: bad operand type for unary +: 'str'" in result
    return result


def test_type_error11a():
    try:
        a = - [1, 2, 3]
        print(a)
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: bad operand type for unary -: 'list'" in result
    return result


def test_type_error11b():
    try:
        a = ~ (1, 2, 3)
        print(a)
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: bad operand type for unary ~: 'tuple'" in result
    return result


def test_type_error12():
    a = (1, 2, 3)
    try:
        a[0] = 0
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "TypeError: 'tuple' object does not support item assignment" in result
    return result


def test_type_error13():
    def fn(*, b=1):
        pass
    try:
        fn(1)
    except Exception:
        friendly_traceback.explain(redirect="capture")
        result = friendly_traceback.get_output()
        assert "TypeError: fn() takes 0 positional arguments but 1 was given" in result
        return result


def test_type_error14():
    def fn(a, b, c):
        pass
    try:
        fn(1)
    except Exception:
        friendly_traceback.explain(redirect="capture")
        result = friendly_traceback.get_output()
        assert "TypeError: fn() missing 2 required positional argument" in result
        return result


def test_type_error15():
    try:
        _ = (1, 2)(3, 4)
    except Exception:
        friendly_traceback.explain(redirect="capture")
        result = friendly_traceback.get_output()
        assert "TypeError: 'tuple' object is not callable" in result
        return result


def test_type_error15a():
    try:
        _ = [1, 2](3, 4)
    except Exception:
        friendly_traceback.explain(redirect="capture")
        result = friendly_traceback.get_output()
        assert "TypeError: 'list' object is not callable" in result
        return result


if __name__ == "__main__":
    print(test_type_error1a())
