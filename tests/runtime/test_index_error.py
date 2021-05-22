import friendly


def test_Short_tuple():
    a = (1, 2, 3)
    b = [1, 2, 3]
    try:
        print(a[3], b[2])
    except IndexError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "IndexError: tuple index out of range" in result
    if friendly.get_lang() == "en":
        assert "The valid index values of" in result
    return result, message


def test_Long_list():
    a = list(range(40))
    b = tuple(range(50))
    try:
        print(a[60], b[0])
    except IndexError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "IndexError: list index out of range" in result
    if friendly.get_lang() == "en":
        assert "The valid index values of" in result
    return result, message


if __name__ == "__main__":
    print(test_index_error1()[0])
    print(test_index_error2()[0])
