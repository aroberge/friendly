"""Simple GUI tools. Could almost certainly be greatly improved.

"""
import tkinter as tk
import tokenize

from io import StringIO
from tkinter import filedialog


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
        self.after(60, self.redraw)
