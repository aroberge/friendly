import friendly_traceback
import sys

friendly_traceback.set_lang("en")

# We use a dict with indices instead of a list to make it easier to
# figure out quickly which cause correspond to which test case.
causes = {
    1: "assign a value to a Python keyword",
    2: "'if' but forgot to add a colon ':'",
    3: "you wrote a 'while' loop but\n    forgot to add a colon ':' at the end",
    4: "wrote 'else if' instead",
    5: "wrote 'elseif' instead",
    6: "you tried to define a function or method",
    7: "you tried to define a function or method",
    8: "you tried to define a function or method",
    9: "what Python calls a 'literal'",
    10: "import X from Y",
}


def test_syntax_errors():
    for i in range(1, 11):
        try:
            exec("from . import raise_syntax_error%d" % i)
        except Exception:
            friendly_traceback.explain(*sys.exc_info(), redirect="capture")
        result = friendly_traceback.get_output()
        assert "SyntaxError" in result, "SyntaxError identified correctly"
        assert causes[i] in result, "Cause %s identified correctly" % i


if __name__ == "__main__":
    print("Can only run with pytest")
