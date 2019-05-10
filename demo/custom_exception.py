"""custom_exception.py"""

# Note: in this demo, we do not include translations.
import os.path


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
        self.lineno = 43  # this line is flagged artificially!
        # Normally, we could never predict where a SyntaxError would arise...


if __name__ == "__main__":
    print("Run custom_exception_demo.py instead")
