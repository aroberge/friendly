import friendly_traceback


def test_index_error1():
    a = (1, 2, 3)
    b = [1, 2, 3]
    try:
        print(a[3], b[2])
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "WARNING" in result, "Internal error found."
    assert "IndexError: tuple index out of range" in result
    return result, message


def test_index_error2():
    a = list(range(40))
    b = tuple(range(50))
    try:
        print(a[50], b[0])
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "WARNING" in result, "Internal error found."
    assert "IndexError: list index out of range" in result
    return result, message


if __name__ == "__main__":
    print(test_index_error1()[0])
    print(test_index_error2()[0])
