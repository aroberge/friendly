"""Contains a function that should raise NameError"""
# flake8: noqa

def test():
    """Should raise NameError"""
    b = c
    d = 3

if __name__ == "__main__":
    import friendly_traceback
    friendly_traceback.install()
    test()
