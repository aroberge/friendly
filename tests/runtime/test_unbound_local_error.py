# More complex example than needed - used for documentation
import friendly_traceback

spam_missing_global = 1


def outer_missing_global():
    def inner():
        spam_missing_global += 1

    inner()


def outer_missing_nonlocal():
    spam_missing_nonlocal = 1

    def inner():
        spam_missing_nonlocal += 1

    inner()


def test_unbound_local_error_missing_global():
    """Should raise UnboundLocalError"""

    try:
        outer_missing_global()
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "WARNING" in result, "Internal error found."
    assert (
        "UnboundLocalError: local variable 'spam_missing_global' referenced" in result
    )
    if friendly_traceback.get_lang() == "en":
        assert (
            "Did you forget to add `global spam_missing_global`?"
            in result
        )
    return result, message


def test_unbound_local_error_missing_nonlocal():
    """Should raise UnboundLocalError"""

    try:
        outer_missing_nonlocal()
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert not "WARNING" in result, "Internal error found."
    assert (
        "UnboundLocalError: local variable 'spam_missing_nonlocal' referenced" in result
    )
    if friendly_traceback.get_lang() == "en":
        assert (
            "Did you forget to add `nonlocal spam_missing_nonlocal`?"
            in result
        )
    return result, message


if __name__ == "__main__":
    print(test_unbound_local_error_missing_global()[0])
