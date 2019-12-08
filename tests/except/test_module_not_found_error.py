import friendly_traceback


def test_module_not_found_error():
    try:
        import does_not_exist
    except Exception:
        friendly_traceback.explain(redirect="capture")
    result = friendly_traceback.get_output()
    assert "ModuleNotFoundError: No module named 'does_not_exist'" in result
    if friendly_traceback.get_lang() == 'en':
        assert "module that cannot be found is 'does_not_exist'." in result
    return result


if __name__ == "__main__":
    print(test_module_not_found_error())
