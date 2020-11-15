import friendly_traceback


def test_module_not_found_error():
    try:
        import Tkinter
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "debug_warning" in result, "Internal error found."
    assert "ModuleNotFoundError: No module named 'Tkinter'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `tkinter`" in result
    return result, message


if __name__ == "__main__":
    print(test_module_not_found_error()[0])
