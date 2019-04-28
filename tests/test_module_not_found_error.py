import friendly_traceback
import sys


def test_module_not_found_error():
    try:
        import does_not_exist
    except Exception:
        friendly_traceback.explain(*sys.exc_info(), redirect="capture")
    result = friendly_traceback.get_output()
    assert "ModuleNotFoundError" in result
    return result


if __name__ == "__main__":
    print(test_module_not_found_error())
