"""custom_exception.py

Showing how to create exceptions that have all the information
needed to be completely processed by Friendly-traceback.
"""

# Our demo exceptions are translated - this is not required for
# exceptions to be interpreted correctly by Friendly-traceback
from demo_gettext import demo_lang


# Best practice: everything here should "work" with a regular
# Python program, without Friendly-traceback being installed.
try:
    import friendly_traceback

    def set_lang():
        """Sets the language used by Friendly-traceback to be also
           used by the custom exceptions."""
        # Only required for exceptions that are translated like is
        # the case for this custom example
        lang = friendly_traceback.get_lang()
        if lang != demo_lang.lang:
            demo_lang.install(lang=lang)
            print("Set lang to", lang)


except Exception:

    def set_lang():
        pass


demo_lang.install()


class MyBaseException(Exception):
    """A basic custom exception."""

    def __init__(self, *args):
        set_lang()
        _ = demo_lang.translate
        self.msg = args[0]
        if len(args) > 1:
            self.args = args[1]
        self.friendly = {"header": _("My CustomException:")}

    def __str__(self):
        return f"{self.__class__.__name__}: {self.msg}"


class MyException1(MyBaseException):
    """The only known information about this custom exception is some
       generic information.
    """

    def __init__(self, *args):
        super().__init__(*args)
        set_lang()
        _ = demo_lang.translate
        self.friendly["generic"] = _(
            "Some generic information about this exception.\n"
            "This exception does not include specific information.\n"
        )


class MyException2(MyBaseException):
    """For this exception, we know both a generic explanation as well as
       a specific explanation (cause) which we can determine from the
       arguments.
    """

    def __init__(self, *args):
        super().__init__(*args)
        set_lang()
        _ = demo_lang.translate
        self.friendly["generic"] = _("Some generic information about this exception.\n")
        self.friendly["cause_header"] = _("The cause is:")
        self.friendly["cause"] = _("Specific cause: {args}\n").format(args=args[1])


# Most programs should NOT need to define their own SyntaxErrors.
# In Python, a SyntaxError is raised when Python cannot process the file
# However, some custom applications (like AvantPy) may need to define
# their own exceptions which are effectively like SyntaxErrors.
# In Python a SyntaxError is expected to include some specific arguments,
# which we artificially set below.


class MyException3(MyBaseException, SyntaxError):
    def __init__(self, *args):
        super().__init__(*args)

        import os.path

        set_lang()
        _ = demo_lang.translate
        self.friendly["generic"] = _("This exception is subclassed from SyntaxError\n")
        self.filename = os.path.abspath(__file__)
        self.offset = 25
        self.lineno = 101  # this line is flagged artificially!
        # Normally, we could never predict where a SyntaxError would arise...


if __name__ == "__main__":
    print("Run custom_exception_demo.py instead")
