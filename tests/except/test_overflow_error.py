import friendly_traceback


def test_overflow_error():
    try:
        2. ** 1600
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "OverflowError" in result
    return result


if __name__ == "__main__":
    print(test_overflow_error())
