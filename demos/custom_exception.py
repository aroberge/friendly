"""custom_exception.py"""

import os.path

from demo_gettext import current_lang

try:
    import friendly_traceback

    friendly_exists = True
except Exception:
    friendly_exists = False


if friendly_exists:

    def set_lang():
        lang = friendly_traceback.get_lang()
        if lang != current_lang.lang:
            current_lang.install(lang=lang)
            print("Set lang to", lang)


else:

    def set_lang():
        pass


current_lang.install()


class MyBaseException(Exception):
    """Custom exception"""

    def __init__(self, *args):
        set_lang()
        _ = current_lang.translate
        self.msg = args[0]
        if len(args) > 1:
            self.args = args[1]
        self.friendly = {"header": _("My CustomException:")}

    def __str__(self):
        return f"{self.__class__.__name__}: {self.msg}"


class MyException1(MyBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        set_lang()
        _ = current_lang.translate
        self.friendly["generic"] = _(
            "Some generic information about this exception.\n"
            "This exception does not include specific information.\n"
        )


class MyException2(MyBaseException):
    def __init__(self, *args):
        super().__init__(*args)
        set_lang()
        _ = current_lang.translate
        self.friendly["generic"] = _("Some generic information about this exception.\n")
        self.friendly["cause_header"] = _("The cause is:")
        self.friendly["cause"] = _("Specific cause: {args}\n").format(args=args[1])


class MyException3(MyBaseException, SyntaxError):
    def __init__(self, *args):
        super().__init__(*args)
        set_lang()
        _ = current_lang.translate
        self.friendly["generic"] = _("This exception is subclassed from SyntaxError\n")
        self.filename = os.path.abspath(__file__)
        self.offset = 25
        self.lineno = 77  # this line is flagged artificially!
        # Normally, we could never predict where a SyntaxError would arise...


if __name__ == "__main__":
    print("Run custom_exception_demo.py instead")
