import friendly_traceback

# TODO: make sure that all these cases are captured in the documentation


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
