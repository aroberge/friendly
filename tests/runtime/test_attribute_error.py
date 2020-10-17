import friendly_traceback


def test_attribute_error():
    class A:
        pass

    A()
    try:
        A.x
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "AttributeError: type object 'A' has no attribute 'x'" in result
    if friendly_traceback.get_lang() == "en":
        assert "In your program, the object is `A` and the attribute is `x`." in result
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
        assert "Perhaps you meant to write `ascii_lowercase`" in result
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
            "Instead of writing `cost`, perhaps you meant one of the following:\n"
            in result
        )
    assert "`cos`, `cosh`" in result
    assert not "acosh" in result
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


if __name__ == "__main__":
    print(test_attribute_error()[0])
