"""In this file, we test to ensure that the output of
run_code is as expected. The tests we do here
are almost identical to those for check_syntax,
found in test_check_syntax.py

We also test to ensure that run_code does not accidently
change any existing error handling settings.

"""

import friendly_traceback as friendly


def test_run_code():
    # set-up
    bad_code_syntax = "True = 1"
    bad_code_exec = "a = b"  # Not a syntax error, but a NameError
    good_code = "c = 1"

    friendly.set_stream("capture")
    original_level = friendly.get_level()
    installed = friendly.is_installed()
    # ----- end of set-up

    # When a SyntaxError is raised, run_code returns False

    assert not friendly.run_code(source=bad_code_syntax)
    result = friendly.get_output()  # content is flushed
    assert "Python exception" in result
    assert "SyntaxError" in result

    assert not friendly.get_output()  # confirm that content was flushed

    assert not friendly.run_code(source=bad_code_exec)
    result = friendly.get_output()
    assert "Python exception" in result
    assert "NameError" in result

    assert friendly.run_code(source=good_code)
    assert not friendly.get_output()  # no new exceptions recorded

    try:
        exec(bad_code_syntax, {})
    except Exception:
        assert not friendly.get_output()

    # When friendly-traceback is not installed, a call to run_code
    # will end with level set to 0, which corresponds to normal Python
    # tracebacks
    friendly.uninstall()
    friendly.run_code(source=bad_code_syntax)
    assert friendly.get_level() == 0
    friendly.run_code(source=bad_code_syntax, level=4)
    assert friendly.get_level() == 0

    # When friendly-traceback is "installed", a call to run_code
    # leaves its level unchanged.
    friendly.install()

    friendly.set_level(3)
    friendly.run_code(source=bad_code_syntax)
    assert friendly.get_level() == 3
    friendly.run_code(source=bad_code_syntax, level=4)
    assert friendly.get_level() == 3

    # Clean up and restore for other tests
    friendly.get_output()
    friendly.set_stream(None)
    if installed:
        friendly.uninstall()
    friendly.set_level(original_level)


if __name__ == "__main__":
    test_run_code()
    print("Success!")
