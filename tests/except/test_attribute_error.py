import friendly_traceback


def test_attribute_error():
    class A:
        pass

    A()
    try:
        A.x
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "AttributeError: type object 'A' has no attribute 'x'" in result
    if friendly_traceback.get_lang() == "en":
        assert "In your program, the object is 'A' and the attribute is 'x'." in result
    return result


if __name__ == "__main__":
    print(test_attribute_error())
