import friendly


def test_Urllib_error():
    from urllib import request, error
    try:
        request.urlopen("http://does_not_exist")
    except error.URLError as e:
        message = str(e)
        friendly.explain_traceback(redirect="capture")
    result = friendly.get_output()

    assert "URLError" in result
    if friendly.get_lang() == "en":
        assert "An exception of type `URLError` is a subclass of `OSError`." in result
        assert "I suspect that you are trying to connect to a server" in result
    return result, message


if __name__ == "__main__":
    print(test_Generic()[0])
