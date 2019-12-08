import friendly_traceback


def test_file_not_found_error():
    try:
        open("does_not_exist")
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert (
        "FileNotFoundError: [Errno 2] No such file or directory: 'does_not_exist'"
        in result
    )
    if friendly_traceback.get_lang() == 'en':
        assert "that cannot be found is 'does_not_exist'." in result
    return result


if __name__ == "__main__":
    print(test_file_not_found_error())
