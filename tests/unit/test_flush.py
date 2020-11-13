import friendly_traceback


def test_flush():
    try:
        b = c
    except Exception:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output(flush=False)
    assert "NameError: name 'c' is not defined" in result
    result1 = friendly_traceback.get_output()  # flushes
    assert "NameError: name 'c' is not defined" in result1
    result2 = friendly_traceback.get_output()  # returns empty string
    assert not result2
    return result, result2


if __name__ == "__main__":
    result, result2 = test_flush()
    print("Before flush:\n", "-" * 50)
    print(result)
    print("=" * 50, "\nAfter flush, should have empty string:\n")
    print(repr(result2))
