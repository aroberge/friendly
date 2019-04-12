"""Should raise TabError"""
# tab character embedded in file


def test_tab_error2():
    if True:
	pass


if __name__ == "__main__":
    import friendly_traceback
    friendly_traceback.install()
    test_tab_error2()
