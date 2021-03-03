from .my_gettext import current_lang


def info():
    _ = current_lang.translate
    return _(
        "If you want to use Friendly-traceback with Mu's REPL, use\n\n"
        "from friendly_traceback.mu_repl import *\n\n"
        "If you wish to use to run a program, add\n\n"
        "from friendly_traceback import *\n"
        "install()\n\n"
        "at the beginning of your program.\n"
    )


print(info())
