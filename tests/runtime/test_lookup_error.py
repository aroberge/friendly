import friendly


def test_Generic():
    try:
        # LookupError is the base class for KeyError and IndexError.
        # It should normally not be raised by user code,
        # other than possibly codecs.lookup(), which is why we raise
        # it directly here for our example.
        raise LookupError("Fake message")
    except Exception as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "LookupError" in result
    if friendly.get_lang() == "en":
        assert "`LookupError` is the base class for" in result
    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
