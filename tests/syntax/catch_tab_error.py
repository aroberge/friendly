import friendly_traceback

def test_tab_error():
    try:
        try:
            from . import raise_tab_error  # for pytest
        except ImportError:
            import raise_tab_error  # noqa
    except Exception:
        friendly_traceback.explain(redirect="capture")

    result = friendly_traceback.get_output()
    assert "TabError: inconsistent use of tabs and spaces in indentation" in result
    return result


if __name__ == "__main__":
    result = test_tab_error()
    print(result)
