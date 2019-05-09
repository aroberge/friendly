"""custom_exception.py"""

# Note: in this demo project, we do not include translations.
import os.path
import sys
import friendly_traceback

friendly_traceback.install()  # sets up excepthook; used in the very last case


class MyBaseException(Exception):
    """Custom exception"""

    def __init__(self, *args):
        self.msg = args[0]
        if len(args) > 1:
            self.args = args[1]
        self.friendly = {"header": "MyCustomException:"}

    def __str__(self):
        return f"{self.__class__.__name__}: {self.msg}"


class MyException1(MyBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.friendly["generic"] = (
            "Some generic information about this exception.\n"
            "This exception does not include specific information.\n"
        )


class MyException2(MyBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        self.friendly["generic"] = "Some generic information about this exception.\n"
        self.friendly["cause_header"] = "The cause is:"
        self.friendly["cause"] = f"Specific cause: {args[1]}\n"


class MyException3(MyBaseException, SyntaxError):
    def __init__(self, *args):
        super().__init__(*args)
        self.friendly["generic"] = "This exception is subclassed from SyntaxError\n"
        self.filename = os.path.abspath(__file__)
        self.offset = 25
        self.lineno = 46  # this line is flagged!


try:
    raise MyException1("A message")
except Exception:
    friendly_traceback.explain(*sys.exc_info())

print("=" * 50)
input("Press enter for second exception")
print("-" * 50)
try:
    raise MyException2("Something went wrong", (1, 2, 3))
except Exception:
    friendly_traceback.explain(*sys.exc_info())

print("=" * 50)
input("Press enter for third exception")
print("-" * 50)
try:
    raise MyException3("Subclass of SyntaxError", (1, 2, 3))
except Exception:
    friendly_traceback.explain(*sys.exc_info())

print("=" * 50)
input("Press enter for fourth exception")
print("-" * 50)
a = 1
try:
    b = a + c  # noqa
except Exception:
    friendly_traceback.explain(*sys.exc_info())


print("=" * 50)
input("Press enter the last exception caught by excepthook")
print("-" * 50)
raise MyException2("A final case", (1, 2, 3))
