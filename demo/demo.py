"""demo.py"""

# Note: in this demo project, we do not include translations.

import friendly_traceback

friendly_traceback.install()


class MyBaseException(Exception):
    """Custom exception"""

    def __init__(self, msg, *args):
        self.msg = msg
        self.args = args
        self.friendly = {"header": "MyCustomException:"}

    def __str__(self):
        return f"{self.__class__.__name__}: {self.msg}"


class MyException1(MyBaseException):
    def __init__(self, msg, *args):
        super().__init__(msg, *args)
        self.friendly["generic"] = (
            "Some generic information about this exception.\n"
            "This exception does not include specific information.\n"
        )


raise MyException1("A message")
