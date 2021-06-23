# More complex example than needed - used for documentation
import friendly

spam_missing_global = 1
spam_missing_both = 1

def outer_missing_global():
    def inner():
        spam_missing_global += 1
    inner()

def outer_missing_nonlocal():
    spam_missing_nonlocal = 1
    def inner():
        spam_missing_nonlocal += 1
    inner()

def outer_missing_both():
    spam_missing_both = 2
    def inner():
        spam_missing_both += 1
    inner()


def test_Missing_global():
    try:
        outer_missing_global()
    except UnboundLocalError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "local variable 'spam_missing_global' referenced" in result
    if friendly.get_lang() == "en":
        assert (
            "Did you forget to add `global spam_missing_global`?\n"
            in result
        )
    return result, message


def test_Missing_nonlocal():
    try:
        outer_missing_nonlocal()
    except UnboundLocalError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "local variable 'spam_missing_nonlocal' referenced" in result
    if friendly.get_lang() == "en":
        assert (
            "Did you forget to add `nonlocal spam_missing_nonlocal`?\n"
            in result
        )
    return result, message


def test_Missing_both():
    try:
        outer_missing_both()
    except UnboundLocalError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "local variable 'spam_missing_both' referenced" in result
    if friendly.get_lang() == "en":
        assert  "either `global spam_missing_both`" in result
        assert  "`nonlocal spam_missing_both`" in result

    return result, message


def test_Typo_in_local():
    
    def test1():
        alpha1 = 1
        alpha2 += 1
        
    try:
        test1()
    except UnboundLocalError:
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()
    
    assert "local variable 'alpha2' referenced before assignment" in result
    if friendly.get_lang() == "en":
        assert "similar name `alpha1` was found" in result

    def test2():
        alpha1 = 1
        alpha2 = 1
        alpha3 += 1

    try:
        test2()
    except UnboundLocalError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "local variable 'alpha3' referenced before assignment" in result
    if friendly.get_lang() == "en":
        assert "perhaps you meant one of the following" in result

    return result, message


if __name__ == "__main__":
    print(test_Missing_global()[0])
