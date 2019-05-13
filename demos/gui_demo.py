"""Simple GUI demo showing how to print the normal traceback and
the friendly traceback in different places.

When run from a shell/command line, the normal Python traceback (or
a suitable approximation) will be printed in that console, whereas the
formatted "friendly traceback" will appear in a text box.

"""
import tkinter as tk

import _gui

from demo_gettext import demo_lang  # this demo includes its own translations
import friendly_traceback

# set up the translations for this demo
demo_lang.install()

# Note: there is no point to do friendly_traceback.install() in this program
# since exceptions would be intercepted by Tkinter; see the run() method below

# However, we may wish to ensure that this file does not show in
# the traceback results, so that it looks like tracebacks running from
# Python instead of from this program.

friendly_traceback.utils.add_excluded_path(__file__)


class App(_gui.App):
    def __init__(self, master=None):
        super().__init__(master=master)
        friendly_traceback.set_formatter(formatter=self.formatter)

    def change_lang(self, event=None):
        """Keeping all the translations in sync"""
        lang = self.lang.get()
        friendly_traceback.set_lang(lang)
        demo_lang.install(lang)
        self.set_ui_lang()

    def set_ui_lang(self):
        _ = demo_lang.translate
        self.menubar.entryconfigure(1, label=_("Open"))
        self.menubar.entryconfigure(2, label=_("Save"))
        self.run_btn.config(text=_("Run"))

    def run(self, event=None):
        # Since we run this from a Tkinter function, any sys.excepthook
        # will be ignored - hence, we need to catch the tracebacks locally.
        try:
            friendly_traceback.run_script(self.filename)
        except Exception:
            friendly_traceback.explain()

    def formatter(self, info, level=None):
        """Our custom formatter.

        A friendly-traceback formatter is expected to return a string which
        will then be printed to the pre-defined stream (usually sys.stderr).

        Note: a friendly-formatter will be passed two arguments, one of which
        we simply ignore here.
        """
        # being lazy: we use the default formatter for the friendly-traceback
        # without including the Python traceback
        text = "\n".join(friendly_traceback.formatters.default(info))

        # This is then inserted to an editor which, in its normal state,
        # could be edited. We make it "read only" by setting its state to
        # "DISABLED" after inserting the text.
        # Note that the text inserted here
        self.friendly_output.text_area.config(state=tk.NORMAL)
        self.friendly_output.insert_text(text)
        self.friendly_output.text_area.config(state=tk.DISABLED)

        # Making sure the display is updated
        self.update_idletasks()
        return str(info["simulated_python_traceback"])


def main():
    root = tk.Tk()
    root.geometry("900x600+200+200")
    root.minsize(600, 600)
    app = App(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
