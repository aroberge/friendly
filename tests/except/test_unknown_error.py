import friendly_traceback


class MyException(Exception):
    pass


def test_unknown_error():
    try:
        raise MyException("Some informative message about an unknown exception.")
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "Some informative message" in result
    if friendly_traceback.get_lang() == 'en':
        assert "Please report this example" in result
    return result


if __name__ == "__main__":
    print(test_unknown_error())
