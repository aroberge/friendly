# More complex example than needed - used for documentation
import friendly

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


def test_Missing_global():
    """Should raise UnboundLocalError"""

    try:
        outer_missing_global()
    except UnboundLocalError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert (
        "UnboundLocalError: local variable 'spam_missing_global' referenced" in result
    )
    if friendly.get_lang() == "en":
        assert (
            "Did you forget to add `global spam_missing_global`?\n"
            in result
        )
    return result, message


def test_Missing_nonlocal():
    """Should raise UnboundLocalError"""

    try:
        outer_missing_nonlocal()
    except UnboundLocalError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert (
        "UnboundLocalError: local variable 'spam_missing_nonlocal' referenced" in result
    )
    if friendly.get_lang() == "en":
        assert (
            "Did you forget to add `nonlocal spam_missing_nonlocal`?\n"
            in result
        )
    return result, message


if __name__ == "__main__":
    print(test_Missing_global()[0])
