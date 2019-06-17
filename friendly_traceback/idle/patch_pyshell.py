"""Patches idlelib's pyshell.py to replace the interpreter by
our custom version.
"""
import os
import tokenize
import sys

import friendly_traceback

from friendly_traceback import set_stream
from friendly_traceback.console import FriendlyConsole, banner

import idlelib.pyshell as pyshell


friendly_traceback.exclude_file_from_traceback(__file__)
friendly_traceback.exclude_file_from_traceback(pyshell.__file__)

old_PyShell = pyshell.PyShell


class MyPyShell(old_PyShell):
    def begin(self):
        self.text.mark_set("iomark", "insert")
        self.resetoutput()
        client = self.interp.start_subprocess()
        if not client:
            self.close()
            return False

        self.write(banner)  # only change for Friendly-traceback
        self.text.focus_force()
        self.showprompt()
        import tkinter

        tkinter._default_root = None  # 03Jan04 KBK What's this?
        return True


pyshell.PyShell = MyPyShell
pyshell.use_subprocess = True
old_ModifiedInterpreter = pyshell.ModifiedInterpreter


class MyModifiedInterpreter(FriendlyConsole, old_ModifiedInterpreter):
    def __init__(self, tkconsole):
        self.tkconsole = tkconsole
        locals = sys.modules["__main__"].__dict__
        FriendlyConsole.__init__(self, locals=locals)
        set_stream(self.write)

        self.save_warnings_filters = None
        self.restarting = False
        self.subprocess_arglist = None
        self.port = pyshell.PORT
        self.original_compiler_flags = self.compile.compiler.flags

    def start_subprocess(self):
        self.rppcclt = super().start_subprocess()
        self.rpcclt.register("friendly_traceback", friendly_traceback)
        self.rpcclt.register("interp", self)
        return self.rppcclt

    def execfile(self, filename, source=None):
        "Execute an existing file"
        if source is None:
            with tokenize.open(filename) as fp:
                source = fp.read()

                source = (
                    f"__file__ = r'''{os.path.abspath(filename)}'''\n"
                    + source
                    + "\ndel __file__"
                )
        try:
            code = compile(source, filename, "exec")
        except (OverflowError, SyntaxError):
            self.tkconsole.resetoutput()
            print(
                "*** Error in script or command!\n"
                "Traceback (most recent call last):",
                file=self.tkconsole.stderr,
            )
            FriendlyConsole.showsyntaxerror(self, filename)
            self.tkconsole.showprompt()
        else:
            self.runcode(code)

    def showsyntaxerror(self, filename=None):
        """Override parent method"""
        FriendlyConsole.showsyntaxerror(self)
        self.tkconsole.resetoutput()
        self.tkconsole.showprompt()

    def showtraceback(self):
        "Extend base class method to reset output properly"
        FriendlyConsole.showtraceback(self)
        self.tkconsole.resetoutput()
        self.tkconsole.showprompt()

    def runcode(self, code):
        "Override base class method"
        if self.tkconsole.executing:
            self.interp.restart_subprocess()
        self.checklinecache()
        if self.save_warnings_filters is not None:
            pyshell.warnings.filters[:] = self.save_warnings_filters
            self.save_warnings_filters = None
        debugger = self.debugger
        try:
            self.tkconsole.beginexecuting()
            if not debugger and self.rpcclt is not None:
                self.active_seq = self.rpcclt.asyncqueue("exec", "runcode", (code,), {})
            elif debugger:
                debugger.run(code, self.locals)
            else:
                exec(code, self.locals)
        except SystemExit:
            if not self.tkconsole.closing:
                if pyshell.tkMessageBox.askyesno(
                    "Exit?",
                    "Do you want to exit altogether?",
                    default="yes",
                    parent=self.tkconsole.text,
                ):
                    raise
                else:
                    self.showtraceback()
            else:
                raise
        except Exception:
            self.showtraceback()


pyshell.ModifiedInterpreter = MyModifiedInterpreter
main = pyshell.main
