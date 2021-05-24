import friendly


def test_Generic():
    try:
        # We raise it explicitly, rather than with the keyword assert, since
        # we don't want pytest to rewrite out test.
        raise AssertionError("Fake message")
    except AssertionError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "AssertionError" in result
    if friendly.get_lang() == "en":
        assert "an `AssertionError` is raised." in result
    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
