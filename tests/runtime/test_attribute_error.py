import friendly

# TODO: make sure that all these cases are captured in the documentation

# Need to add more cases, ensuring that correct object is always identified

# a = [1, 2, 3]
# b = 3, 4, 5

# b[0] > a.max  --> max(a)
# b.min == a[0]  --> min(b)
# a.length  --> len(a)
# a.len --> len(a)

# a.b -> a, b ?


def test_Generic():
    # Generic - no additional explanation
    class A:
        pass

    try:
        A.x  # testing type
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AttributeError: type object 'A' has no attribute 'x'" in result
    if friendly.get_lang() == "en":
        assert "The object `A` has no attribute" in result

    try:
        a = A()
        a.x  # Testing instance
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AttributeError: 'A' object has no attribute 'x'" in result
    if friendly.get_lang() == "en":
        assert "The object `a` has no attribute" in result
    return result, message


def test_Object_attribute_typo():
    #
    try:
        a = [1, 2, 3]
        a.appendh(4)
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AttributeError: 'list' object has no attribute 'appendh'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `append`" in result
    return result, message


def test_Use_builtin():
    #
    try:
        a = [1, 2, 3]
        a.length()
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AttributeError: 'list' object has no attribute 'length'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `len(a)`" in result
    return result, message


def test_Use_synonym():
    #
    try:
        a = [1, 2, 3]
        a.add(4)
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AttributeError: 'list' object has no attribute 'add'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `append`" in result
    return result, message



def test_Module_attribute_typo():
    import string

    try:
        string.ascii_lowecase
    except Exception as e:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AttributeError: module 'string' has no attribute 'ascii_lowecase'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `ascii_lowercase`" in result

    import math

    try:
        math.cost
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AttributeError: module 'math' has no attribute 'cost'" in result
    if friendly.get_lang() == "en":
        assert (
            "Instead of writing `math.cost`, perhaps you meant to write one of"
            in result
        )
    assert "cos, cosh" in result
    assert not "acosh" in result
    return result, message


def test_Shadow_stdlib_module():
    import turtle

    try:
        turtle.Pen
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AttributeError: module 'turtle' has no attribute 'Pen'" in result
    if friendly.get_lang() == "en":
        assert (
            "There is also a module named `turtle` in Python's standard library."
            in result
        )
    return result, message


def test_Nonetype():
    a = None
    try:
        a.b
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "'NoneType' object has no attribute 'b'" in result
    if friendly.get_lang() == "en":
        assert "for a variable whose value is `None`" in result

    return result, message


def test_Perhaps_comma():
    abcd = "hello"
    defg = "world"

    # fmt: off
    try:
        a = [abcd
        .defg]
    # fmt: on
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "'str' object has no attribute 'defg'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean to separate object names by a comma" in result
    return result, message


def test_Builtin_function():
    text = 'Hello world!'
    try:
        len.text
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "'builtin_function_or_method'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `len(text)`" in result
    return result, message


def test_Builtin_module_with_no_file():
    """Issue 116"""
    import sys

    try:
        sys.foo
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "module 'sys' has no attribute 'foo'" in result
    if friendly.get_lang() == "en":
        assert "Python tells us" in result
    return result, message


def test_Using_slots():
    """Issue 141"""

    class F:
        __slots__ = ["a"]

    f = F()
    try:
        f.b = 1
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "'F' object has no attribute 'b'" in result
    if friendly.get_lang() == "en":
        assert "object `f` uses `__slots__`" in result
    return result, message


def test_Tuple_by_accident():
    something = "abc",  # note trailing comma
    try:
        something.upper()
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "'tuple' object has no attribute 'upper'" in result
    if friendly.get_lang() == "en":
        assert "Did you write a comma" in result

    return result, message


def test_Attribute_from_other_module():
    import math
    import keyword

    try:
        keyword.pi
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")

    result = friendly.get_output()
    assert "module 'keyword' has no attribute 'pi'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `math`?" in result

    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
