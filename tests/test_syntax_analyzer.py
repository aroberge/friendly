"""test_syntax_analyzer"""

from friendly_traceback.analyze_syntax import analyze_last_line


def test():
    a = analyze_last_line
    assert a("class True") == "class missing colon"
    assert a("def True") == "def missing colon"
    assert a("if True") == "if missing colon"
    assert a("elif True") == "elif missing colon"
    assert a("else True") == "else missing colon"
    assert a("for True") == "for missing colon"
    assert a("while True") == "while missing colon"
    assert a("try True") == "try missing colon"
    assert a("except True") == "except missing colon"
    assert a("finally True") == "finally missing colon"


if __name__ == '__main__':
    test()
    print("Tests ran successfully")
