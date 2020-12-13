"""In this file, we test to ensure that the output of
check_syntax is as expected.

We also test to ensure that check_syntax does not accidently
change any existing error handling settings.

"""

import friendly_traceback as friendly


def test_check_syntax():
    # set-up
    bad_code_syntax = "True = 1"
    bad_code_exec = "a = b"  # Not a syntax error, but a NameError
    good_code = "c = 1"

    friendly.set_stream("capture")
    original_include = friendly.get_include()
    installed = friendly.is_installed()
    # ----- end of set-up

    # When a SyntaxError is raised, check_syntax returns False

    assert not friendly.editors_helpers.check_syntax(source=bad_code_syntax)
    result = friendly.get_output()  # content is flushed
    assert "SyntaxError" in result

    assert not friendly.get_output()  # confirm that content was flushed

    # When no SyntaxError is raised, check_syntax returns a tuple
    # containing a code object and a file name
    assert friendly.editors_helpers.check_syntax(source=bad_code_exec)
    assert friendly.editors_helpers.check_syntax(source=good_code)
    assert not friendly.get_output()  # no new exceptions recorded

    try:
        exec(bad_code_syntax, {})
    except Exception:
        assert not friendly.get_output()

    # Ensure that a call to check_syntax only install() temporarily
    # if it was not installed before.

    friendly.uninstall()
    friendly.editors_helpers.check_syntax(source=bad_code_syntax)
    assert not friendly.is_installed()
    friendly.editors_helpers.check_syntax(source=bad_code_syntax, include="python_tb")
    assert not friendly.is_installed()

    # When friendly-traceback is "installed", a call to check_syntax
    # leaves its include unchanged.
    friendly.install(redirect="capture")

    friendly.set_include("explain")
    friendly.editors_helpers.check_syntax(source=bad_code_syntax)
    assert friendly.get_include() == "explain"
    friendly.editors_helpers.check_syntax(source=bad_code_syntax, include="python_tb")
    assert friendly.get_include() == "explain"

    # A call to advanced_code_syntax, with a language specified as an argument
    # should leave the previous language unchanged.

    friendly.set_lang("en")
    assert not friendly.editors_helpers.check_syntax(source=bad_code_syntax, lang="fr")
    result = friendly.get_output()
    assert "Une exception de type `SyntaxError`" in result
    assert friendly.get_lang() == "en"

    # Clean up and restore for other tests
    friendly.get_output()
    friendly.set_stream(None)
    if installed:
        friendly.uninstall()
    friendly.set_include(original_include)


if __name__ == "__main__":
    test_check_syntax()
    print("Success!")
