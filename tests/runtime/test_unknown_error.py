import friendly


class MyException(Exception):
    pass


def test_Generic():
    old_debug = friendly.debug_helper.DEBUG
    friendly.debug_helper.DEBUG = False
    try:
        raise MyException("Some informative message about an unknown exception.")
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "Some informative message" in result
    if friendly.get_lang() == "en":
        assert "No information is known about this exception." in result
    friendly.debug_helper.DEBUG = old_debug
    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
