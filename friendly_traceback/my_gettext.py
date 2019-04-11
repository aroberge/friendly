import gettext
import os


class LangState:
    def __init__(self):
        self.lang = None

    def install(self, lang):
        try:
            _lang = gettext.translation(
                lang,
                localedir=os.path.normpath(
                    os.path.join(os.path.dirname(__file__), "locales")
                ),
                languages=[lang],
                fallback=False,
            )
        except FileNotFoundError:
            lang = lang[:2]
            _lang = gettext.translation(
                lang,
                localedir=os.path.normpath(
                    os.path.join(os.path.dirname(__file__), "locales")
                ),
                languages=[lang],
                fallback=True,
            )
        self.lang = _lang.gettext


current_lang = LangState()  # noqa
