"""In this file, we test to ensure that the output of
exec_code is as expected. The tests we do here
are almost identical to those for check_syntax,
found in test_check_syntax.py

We also test to ensure that exec_code does not accidentally
change any existing error handling settings.

"""

import friendly as ft


def test_exec_code():
    # set-up
    bad_code_syntax = "True = 1"
    bad_code_exec = "a = b"  # Not a syntax error, but a NameError
    good_code = "c = 1"

    ft.set_stream("capture")
    original_include = ft.get_include()
    installed = ft.is_installed()
    # ----- end of set-up

    # When a SyntaxError is raised, exec_code returns False

    assert not ft.editors_helpers.exec_code(source=bad_code_syntax)
    result = ft.get_output()  # content is flushed
    assert "SyntaxError" in result

    assert not ft.get_output()  # confirm that content was flushed

    ft.editors_helpers.exec_code(source=bad_code_exec)
    result = ft.get_output()
    assert "NameError" in result

    assert ft.editors_helpers.exec_code(source=good_code)
    assert not ft.get_output()  # no new exceptions recorded

    try:
        exec(bad_code_syntax, {})
    except Exception:
        assert not ft.get_output()

    # Ensure that a call to exec_code only install() temporarily
    # if it was not installed before.
    ft.uninstall()
    ft.editors_helpers.exec_code(source=bad_code_syntax)
    assert not ft.is_installed()
    ft.editors_helpers.exec_code(source=bad_code_syntax, include="no_tb")
    assert not ft.is_installed()

    # When friendly is "installed", a call to exec_code
    # leaves its include unchanged.
    ft.install(redirect="capture")

    ft.set_include("friendly_tb")
    ft.editors_helpers.exec_code(source=bad_code_syntax)
    assert ft.get_include() == "friendly_tb"
    ft.editors_helpers.exec_code(source=bad_code_syntax, include="no_tb")
    assert ft.get_include() == "friendly_tb"

    # A call to exec_code, with a language specified as an argument
    # should leave the previous language unchanged.

    ft.set_lang("en")
    ft.editors_helpers.exec_code(source=bad_code_exec, lang="fr", include="explain")
    result = ft.get_output()
    assert "Une exception `NameError` indique" in result
    assert ft.get_lang() == "en"

    # Clean up and restore for other tests
    ft.get_output()
    ft.set_stream(None)
    if installed:
        ft.uninstall()
    ft.set_include(original_include)


if __name__ == "__main__":
    test_exec_code()
    print("Success!")
