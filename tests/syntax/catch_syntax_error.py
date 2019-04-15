import friendly_traceback
import sys

# We just want to make sure that the files run without being broken
# or deleted.  The true output is created in the docs, when
# we run the trb_... scripts.


def test_syntax_errors():
    for i in range(1, 10):
        try:
            exec("from . import raise_syntax_error%d" % i)
        except Exception:
            friendly_traceback.explain(*sys.exc_info(), redirect="capture")
        result = friendly_traceback.get_output()
        assert "SyntaxError" in result


if __name__ == '__main__':
    print("Can only run with pytest")
