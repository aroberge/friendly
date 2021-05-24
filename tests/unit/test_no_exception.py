import friendly

def test_No_exception(capsys):
    if friendly.get_lang() == "en":
        friendly.explain_traceback()
        captured = capsys.readouterr()
        assert "Nothing to show: no exception recorded." in captured.out
