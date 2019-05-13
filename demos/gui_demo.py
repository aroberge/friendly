"""Simple GUI demo showing how to print the normal traceback and
the friendly traceback in different places.

"""
import keyword
import os
import tkinter as tk

from tkinter import filedialog, ttk

import _gui

from demo_gettext import current_lang  # this demo includes its own translations
import friendly_traceback

# Note: there is no point to do friendly_traceback.install() in this program
# since exceptions would be intercepted by Tkinter; see the run() method below

# However, we may wish to ensure that this file does not show in
# the traceback results, so that it looks like tracebacks running from
# Python instead of from this program.

friendly_traceback.utils.add_excluded_path(__file__)

current_lang.install()


class App(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.master.title("GUI demo")
        self.add_ui()

        self.python_words = set(keyword.kwlist)
        friendly_traceback.set_formatter(formatter=self.formatter)

    def add_ui(self):
        """Adds UI elements to the main window"""
        _ = current_lang.translate

        for r in range(3):
            self.master.rowconfigure(r, weight=1, minsize=20)
        for c in range(5):
            self.master.columnconfigure(c, weight=1, minsize=40)

        self.source_editor = _gui.EditorWidget(self.master, self)
        self.source_editor.grid(row=0, column=0, columnspan=5, sticky="news")

        self.menubar = tk.Menu(self.master)
        self.menubar.add_command(label=_("Open"), command=self.get_source)
        self.menubar.add_command(label=_("Save"), command=self.source_editor.save_file)
        self.master.config(menu=self.menubar)

        self.run_btn = tk.Button(self.master, text=_("Run"), command=self.run)
        self.run_btn.grid(row=1, column=0, sticky="w")
        self.run_btn.config(state=tk.DISABLED)

        self._choice = tk.StringVar()
        self.lang = ttk.Combobox(
            self.master, textvariable=self._choice, values=["en", "fr"]
        )
        self.lang.grid(row=1, column=1, sticky="w")
        self.lang.current(0)
        self.lang.bind("<<ComboboxSelected>>", self.change_lang)
        self.set_ui_lang()

        self.friendly_output = _gui.EditorWidget(self.master, self)
        self.friendly_output.grid(row=2, column=0, columnspan=5, sticky="news")
        self.friendly_output.text_area.config(state=tk.DISABLED, foreground="darkred")

        def do_nothing():
            pass

        self.friendly_output.colorize = do_nothing

    def change_lang(self, event=None):
        lang = self.lang.get()
        friendly_traceback.set_lang(lang)
        current_lang.install(lang)
        self.set_ui_lang()

    def set_ui_lang(self):
        _ = current_lang.translate
        self.menubar.entryconfigure(1, label=_("Open"))
        self.menubar.entryconfigure(2, label=_("Save"))
        self.run_btn.config(text=_("Run"))

    def get_source(self, event=None):
        """Opens a file by looking first from the current directory."""
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(), filetypes=(("Python", "*.py*"),)
        )
        if filename:
            with open(filename, encoding="utf8") as new_file:
                self.source_editor.insert_text(new_file.read())
            self.filename = filename
            self.run_btn.config(state=tk.NORMAL)

    def run(self, event=None):
        # Since we run this from a Tkinter function, any sys.excepthook
        # will be ignored - hence, we need to catch the tracebacks locally.
        try:
            friendly_traceback.run_script(self.filename)
        except Exception:
            friendly_traceback.explain()

    def formatter(self, info, level=None):
        text = "\n".join(friendly_traceback.formatters.default(info))
        self.friendly_output.text_area.config(state=tk.NORMAL)
        self.friendly_output.insert_text(text)
        self.friendly_output.text_area.config(state=tk.DISABLED)
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
