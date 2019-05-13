"""Simple GUI demo showing how to print the normal traceback and
the friendly traceback in different places.

"""
import keyword
import os
import tkinter as tk
import tokenize

from io import StringIO
from tkinter import filedialog, ttk

import friendly_traceback

# Note: there is no point to do friendly_traceback.install() in this program
# since exceptions would be intercepted by Tkinter.
# See the run() method below

from demo_gettext import current_lang


current_lang.install()


class Token:
    """Token as generated from tokenize.generate_tokens written here in
       a more convenient form for our purpose.
    """

    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start_line, self.start_col = token[2]
        self.end_line, self.end_col = token[3]
        # ignore last parameter which is the logical line


class EditorWidget(tk.Frame):
    """A scrollable text editor, that can save files."""

    def __init__(self, parent, parent_frame):
        super().__init__()
        self.parent = parent
        self.parent_frame = parent_frame
        self.frame = tk.Frame(self, width=600, height=600)
        self.text_area = self.init_text_area()
        self.set_horizontal_scroll()
        self.set_vertical_scroll()
        self.linenumbers = TextLineNumbers(self.frame, width=30)
        self.linenumbers.attach(self.text_area)
        self.linenumbers.pack(side="left", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)
        self.text_area.bind("<Key>", self.colorize)
        self.frame.pack(fill="both", expand=True)

    def init_text_area(self):
        text_area = tk.Text(
            self.frame,
            wrap="none",
            width=600,
            height=600,
            padx=10,
            pady=10,
            font="Monaco 11",
        )
        text_area.tag_config("Python", font="Monaco 11 bold", foreground="blue")
        text_area.tag_config(
            "Comment", font="Monaco 11 italic", foreground="forest green"
        )
        return text_area

    def set_horizontal_scroll(self):
        scroll_x = tk.Scrollbar(
            self.frame, orient="horizontal", command=self.text_area.xview
        )
        scroll_x.config(command=self.text_area.xview)
        self.text_area.configure(xscrollcommand=scroll_x.set)
        scroll_x.pack(side="bottom", fill="x", anchor="w")

    def set_vertical_scroll(self):
        # Scroll Bar y For Height
        scroll_y = tk.Scrollbar(self.frame)
        scroll_y.config(command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")

    def insert_text(self, txt):
        """Inserts the text in the editor, replacing any previously existing
           content.
        """
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", txt)
        self.parent.update_idletasks()
        self.colorize()

    def get_text(self):
        """Gets the current content and returns it as a string"""
        # For some reason, an extra "\n" is added, which we need to remove.
        return self.text_area.get("1.0", tk.END)[:-1]

    def colorize(self, event=None):
        """Colorizes the Python keywords and comments.
        """
        content = self.text_area.get("1.0", tk.END)
        try:
            tokens = tokenize.generate_tokens(StringIO(content).readline)
            for tok in tokens:
                token = Token(tok)
                if (
                    token.string in self.parent_frame.python_words
                    and token.type == tokenize.NAME
                ):
                    begin_index = "{0}.{1}".format(token.start_line, token.start_col)
                    end_index = "{0}.{1}".format(token.end_line, token.end_col)
                    self.text_area.tag_add("Python", begin_index, end_index)
                elif token.type == tokenize.COMMENT:
                    begin_index = "{0}.{1}".format(token.start_line, token.start_col)
                    end_index = "{0}.{1}".format(token.end_line, token.end_col)
                    self.text_area.tag_add("Comment", begin_index, end_index)
        except tokenize.TokenError:
            pass

    def save_file(self, event=None):
        """Saves the file currently in the Texteditor"""
        filename = filedialog.asksaveasfilename(filetypes=(("Python", "*.py*"),))
        if filename is not None:
            with open(filename, "w", encoding="utf8") as f:
                data = self.get_text()
                f.write(data)


class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, textwidget):
        self.textwidget = textwidget
        self.redraw()

    def redraw(self, *args):
        """redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, font="Monaco 12")
            i = self.textwidget.index("%s+1line" % i)
        self.after(30, self.redraw)


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
        _ = current_lang.lang

        for r in range(3):
            self.master.rowconfigure(r, weight=1, minsize=20)
        for c in range(5):
            self.master.columnconfigure(c, weight=1, minsize=40)

        self.source_editor = EditorWidget(self.master, self)
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

        self.friendly_output = EditorWidget(self.master, self)
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
        _ = current_lang.lang
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
        return str(info["python_traceback"])


def main():
    root = tk.Tk()
    root.geometry("900x600+200+200")
    root.minsize(600, 600)
    app = App(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
