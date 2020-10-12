# More complex example than needed - used for documentation
import friendly_traceback

b = 2


def outer():
    a = 1

    def inner():
        c = 3
        a = a + b + c

    inner()


def test_unbound_local_error():
    """Should raise UnboundLocalError"""

    try:
        outer()
    except Exception as e:
        message = str(e)
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "UnboundLocalError: local variable 'a' referenced" in result
    if friendly_traceback.get_lang() == "en":
        assert "The variable that appears to cause the problem is `a`." in result
    return result, message


if __name__ == "__main__":
    print(test_unbound_local_error())
