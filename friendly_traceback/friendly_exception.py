from .my_gettext import current_lang


class FriendlyException(Exception):
    def __init__(self, fn_name):
        _ = current_lang.translate

        self.message = (
            "\n\n===========================================\n\n"
            + _(
                "Friendly-traceback: Internal Problem\n"
                "Source: {fn_name}\n"
                "Please report this case.\n"
            ).format(fn_name=fn_name)
            + "\n===========================================\n"
        )
        super().__init__((self.message,))

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message
