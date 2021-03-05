"""In this file, we test to ensure that the output of
check_syntax is as expected.

We also test to ensure that check_syntax does not accidently
change any existing error handling settings.

"""

import friendly_traceback as ft


def test_check_syntax():
    # set-up
    bad_code_syntax = "True = 1"
    bad_code_exec = "a = b"  # Not a syntax error, but a NameError
    good_code = "c = 1"

    ft.set_stream("capture")
    original_include = ft.get_include()
    installed = ft.is_installed()
    # ----- end of set-up

    # When a SyntaxError is raised, check_syntax returns False

    assert not ft.editors_helpers.check_syntax(source=bad_code_syntax)
    result = ft.get_output()  # content is flushed
    assert "SyntaxError" in result

    assert not ft.get_output()  # confirm that content was flushed

    # When no SyntaxError is raised, check_syntax returns a tuple
    # containing a code object and a file name
    assert ft.editors_helpers.check_syntax(source=bad_code_exec)
    assert ft.editors_helpers.check_syntax(source=good_code)
    assert not ft.get_output()  # no new exceptions recorded

    try:
        exec(bad_code_syntax, {})
    except Exception:
        assert not ft.get_output()

    # Ensure that a call to check_syntax only install() temporarily
    # if it was not installed before.

    ft.uninstall()
    ft.editors_helpers.check_syntax(source=bad_code_syntax)
    assert not ft.is_installed()
    ft.editors_helpers.check_syntax(source=bad_code_syntax, include="python_tb")
    assert not ft.is_installed()

    # When friendly-traceback is "installed", a call to check_syntax
    # leaves its include unchanged.
    ft.install(redirect="capture")

    ft.set_include("explain")
    ft.editors_helpers.check_syntax(source=bad_code_syntax)
    assert ft.get_include() == "explain"
    ft.editors_helpers.check_syntax(source=bad_code_syntax, include="python_tb")
    assert ft.get_include() == "explain"

    # A call to advanced_code_syntax, with a language specified as an argument
    # should leave the previous language unchanged.

    ft.set_lang("en")
    assert not ft.editors_helpers.check_syntax(source=bad_code_syntax, lang="fr")
    result = ft.get_output()
    assert "Une exception de type `SyntaxError`" in result
    assert ft.get_lang() == "en"

    # Clean up and restore for other tests
    ft.get_output()
    ft.set_stream(None)
    if installed:
        ft.uninstall()
    ft.set_include(original_include)


if __name__ == "__main__":
    test_check_syntax()
    print("Success!")
