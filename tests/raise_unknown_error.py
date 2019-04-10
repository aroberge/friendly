"""Contains a function that should raise an unknown exception"""
# flake8: noqa

class MyException(Exception):
    pass

def test():
    raise MyException("Some informative message")

if __name__ == "__main__":
    import friendly_traceback
    friendly_traceback.install()
    test()
