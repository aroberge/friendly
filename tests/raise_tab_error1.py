"""Should raise TabError"""

# To avoid accidental transformations of
# tab characters into spaces when editing this file
# we embed this test in a string.


def test_tab_error1():
    exec("""if True:\n        pass\n\tpass""")


if __name__ == "__main__":
    import friendly_traceback
    friendly_traceback.install()
    test_tab_error1()
