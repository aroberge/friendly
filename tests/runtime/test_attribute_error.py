import friendly_traceback

# TODO: make sure that all these cases are captured in the documentation

# Need to add more cases, ensuring that correct object is always identified

# a = [1, 2, 3]
# b = 3, 4, 5

# b[0] > a.max  --> max(a)
# b.min == a[0]  --> min(b)
# a.length  --> len(a)
# a.len --> len(a)

# a.b -> a, b ?


def test_attribute_error():
    class A:
        pass

    try:
        A.x  # testing type
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "AttributeError: type object 'A' has no attribute 'x'" in result
    if friendly_traceback.get_lang() == "en":
        assert "The object of type `A` has no attribute" in result

    try:
        a = A()
        a.x  # Testing instance
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "AttributeError: 'A' object has no attribute 'x'" in result
    if friendly_traceback.get_lang() == "en":
        assert "The object `a` has no attribute" in result
    return result, message


def test_attribute_error2():
    try:
        a = [1, 2, 3]
        a.appendh(4)
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "AttributeError: 'list' object has no attribute 'appendh'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `append`" in result
    return result, message


def test_misspelled_module_attribute():
    import string

    try:
        string.ascii_lowecase
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "AttributeError: module 'string' has no attribute 'ascii_lowecase'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `ascii_lowercase`" in result
    return result, message


def test_misspelled_module_attribute_2():
    import math

    try:
        math.cost
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert ("AttributeError: module 'math' has no attribute 'cost'") in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "Instead of writing `math.cost`, perhaps you meant to write one of"
            in result
        )
    assert "cos, cosh" in result
    assert not "acosh" in result
    return result, message


def test_shadow_stdlib_module():
    import turtle

    try:
        turtle.Pen
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "AttributeError: module 'turtle' has no attribute 'Pen'" in result
    if friendly_traceback.get_lang() == "en":
        assert (
            "There is also a module named `turtle` in Python's standard library."
            in result
        )
    return result, message


def test_nonetype():
    a = None
    try:
        a.b
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "'NoneType' object has no attribute 'b'" in result
    if friendly_traceback.get_lang() == "en":
        assert "for a variable whose value is `None`" in result


def test_perhaps_comma1():
    abcd = 'hello'
    defg = 'world'
    try:
        a = [abcd. defg]
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "'str' object has no attribute 'defg'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean to separate object names by a comma" in result


def test_perhaps_comma2():
    # same as previous, but objects on separate lines
    abcd = 'hello'
    defg = 'world'
    try:
        a = [abcd.
            defg]
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "'str' object has no attribute 'defg'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean to separate object names by a comma" in result

if __name__ == "__main__":
    print(test_attribute_error()[0])
