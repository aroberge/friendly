import friendly_traceback


def test_lookup_error():
    try:
        # LookupError is the base class for KeyError and IndexError.
        # It should normally not be raised by user code,
        # other than possibly codecs.lookup(), which is why we raise
        # it directly here for our example.
        raise LookupError
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "LookupError" in result
    if friendly_traceback.get_lang() == "en":
        assert "`LookupError` is the base class for" in result
    return result, message


if __name__ == "__main__":
    print(test_lookup_error())
