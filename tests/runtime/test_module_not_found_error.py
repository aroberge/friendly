import friendly_traceback


def test_Standard_library_module():
    try:
        import Tkinter
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ModuleNotFoundError: No module named 'Tkinter'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `tkinter`" in result
    return result, message


def test_Not_a_package():

    try:
        import os.xxx
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ModuleNotFoundError: No module named 'os.xxx'" in result
    if friendly_traceback.get_lang() == "en":
        assert "`xxx` cannot be imported" in result

    try:
        import os.open
    except Exception as e:
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ModuleNotFoundError: No module named 'os.open'" in result
    if friendly_traceback.get_lang() == "en":
        assert "`from os import open`" in result

    try:
        import os.pathh
    except Exception as e:
        message = str(e)
        friendly_traceback.explain_traceback(redirect="capture")
    result = friendly_traceback.get_output()
    
    assert "ModuleNotFoundError: No module named 'os.pathh'" in result
    if friendly_traceback.get_lang() == "en":
        assert "Did you mean `import os.path`" in result
    return result, message


if __name__ == "__main__":
    print(test_Standard_library_module()[0])
