"""Should raise TabError"""
# tab character embedded in file


def no_pytest_tab_error2():
    if True:
	pass


if __name__ == "__main__":
    import friendly_traceback
    friendly_traceback.install()
    no_pytest_tab_error2()
