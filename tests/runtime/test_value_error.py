import friendly


def test_Not_enough_values_to_unpack():
    d = (1,)
    try:
        a, b, *c = d
    except ValueError:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert (
        "ValueError: not enough values to unpack (expected at least 2, got 1)" in result
    )
    if friendly.get_lang() == "en":
        assert "a `tuple` of length 1" in result

    try:
        for x, y, z in enumerate(range(3)):
            pass
    except ValueError:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    assert "ValueError: not enough values to unpack (expected 3, got 2)" in result

    d = "ab"
    try:
        a, b, c = d
    except ValueError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ValueError: not enough values to unpack (expected 3, got 2)" in result
    if friendly.get_lang() == "en":
        assert "a string (`str`) of length 2" in result
    return result, message


def test_Too_many_values_to_unpack():
    c = [1, 2, 3]
    try:
        a, b = c
    except ValueError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ValueError: too many values to unpack (expected 2)" in result
    if friendly.get_lang() == "en":
        assert "a `list` of length 3" in result
    return result, message


if __name__ == "__main__":
    print(test_Too_many_values_to_unpack()[0])
