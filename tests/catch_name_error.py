import friendly_traceback
import sys


def test_name_error():
    try:
        from . import raise_name_error  # for pytest
    except ImportError:
        import raise_name_error

    try:
        raise_name_error.test()
    except Exception:
        friendly_traceback.explain(
            *sys.exc_info(), redirect=friendly_traceback.capture
        )
    result = friendly_traceback.get_output(flush=False)
    assert "NameError" in result


if __name__ == '__main__':
    test_name_error()
    print(friendly_traceback.get_output())
