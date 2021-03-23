import friendly


def test_Standard_library_module():
    try:
        import Tkinter
    except ModuleNotFoundError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ModuleNotFoundError: No module named 'Tkinter'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `tkinter`" in result
    return result, message


def test_Not_a_package():

    try:
        import os.xxx
    except ModuleNotFoundError as e:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ModuleNotFoundError: No module named 'os.xxx'" in result
    if friendly.get_lang() == "en":
        assert "`xxx` cannot be imported" in result

    try:
        import os.open
    except ModuleNotFoundError as e:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ModuleNotFoundError: No module named 'os.open'" in result
    if friendly.get_lang() == "en":
        assert "`from os import open`" in result

    try:
        import os.pathh
    except ModuleNotFoundError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "ModuleNotFoundError: No module named 'os.pathh'" in result
    if friendly.get_lang() == "en":
        assert "Did you mean `import os.path`" in result
    return result, message


if __name__ == "__main__":
    print(test_Standard_library_module()[0])
