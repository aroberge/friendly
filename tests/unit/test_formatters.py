import friendly_traceback


def test_all_levels():
    try:
        b = c
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "NameError: name 'c' is not defined" in result

    # Simply ensuring that no exceptions are raised when
    # changing verbosity level
    saved_verbosity = friendly_traceback.get_verbosity()
    friendly_traceback.set_stream("capture")
    for level in range(0, 10):
        friendly_traceback.set_verbosity(level)
        friendly_traceback.show_again()
    friendly_traceback.set_verbosity(saved_verbosity)


if __name__ == "__main__":
    test_all_levels()
