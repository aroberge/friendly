"""console.py

Adaptation of Python's console found in code.py so that it can be
used to show some "friendly" tracebacks.
"""
import builtins
import copy
import os
import platform
from code import InteractiveConsole
import codeop  # need to import to exclude from tracebacks

from . import public_api
from . import source_cache
from .my_gettext import current_lang

from . import friendly_rich

BANNER = "Friendly Console version {}. [Python version: {}]\n".format(
    public_api.__version__, platform.python_version()
)


class FriendlyConsole(InteractiveConsole):
    def __init__(self, locals=None, use_rich=False):
        """This class builds upon Python's code.InteractiveConsole
        so as to provide friendly tracebacks. It keeps track
        of code fragment executed by treating each of them as
        an individual source file.
        """
        public_api.exclude_file_from_traceback(codeop.__file__)
        self.fake_filename = "<friendly-console:%d>"
        self.counter = 1
        self.hints = {}  # Keeps track of type hints
        self.old_locals = {}
        if friendly_rich.rich_available and use_rich:
            self.rich_console = friendly_rich.console
        else:
            self.rich_console = False

        super().__init__(locals=locals)

    def push(self, line):
        """Push a line to the interpreter.

        The line should not have a trailing newline; it may have
        internal newlines.  The line is appended to a buffer and the
        interpreter's runsource() method is called with the
        concatenated contents of the buffer as source.  If this
        indicates that the command was executed or invalid, the buffer
        is reset; otherwise, the command is incomplete, and the buffer
        is left as it was after the line was appended.  The return
        value is True if more input is required, False if the line was dealt
        with in some way (this is the same as runsource()).
        """
        self.buffer.append(line)
        source = "\n".join(self.buffer)

        # Each valid code sample is saved with its own fake filename.
        # They are numbered consecutively to help understanding
        # the traceback history.
        # If self.counter was not updated, it means that the previous
        # code sample was not valid and we reuse the same file name
        filename = self.fake_filename % self.counter
        source_cache.cache.add(filename, source)

        more = self.runsource(source, filename)
        if not more:
            self.resetbuffer()
            self.counter += 1
        return more

    def runsource(self, source, filename="<input>", symbol="single"):
        """Compile and run some source in the interpreter.

        Arguments are as for compile_command().

        One several things can happen:

        1) The input is incorrect; compile_command() raised an
        exception (SyntaxError or OverflowError).  A syntax traceback
        will be printed .

        2) The input is incomplete, and more input is required;
        compile_command() returned None.  Nothing happens.

        3) The input is complete; compile_command() returned a code
        object.  The code is executed by calling self.runcode() (which
        also handles run-time exceptions, except for SystemExit).

        The return value is True in case 2, False in the other cases (unless
        an exception is raised).  The return value can be used to
        decide whether to use sys.ps1 or sys.ps2 to prompt the next
        line.
        """
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            public_api.explain()
            return False

        if code is None:
            # Case 2
            return True

        # Case 3
        self.runcode(code)
        return False

    def runcode(self, code):
        """Execute a code object.

        When an exception occurs, friendly_traceback.explain() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which, unlike the case for the original version in the
        standard library, cleanly exists the program. This is done
        so as to avoid our Friendly-traceback's exception hook to intercept
        it and confuse the users.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.
        """
        _ = current_lang.translate
        try:
            exec(code, self.locals)
        except SystemExit:
            os._exit(1)
        except Exception:
            public_api.explain()

        self.check_for_annotations()
        self.old_locals = copy.copy(self.locals)

    def check_for_annotations(self):
        """Attempts to detect code that uses : instead of = by mistake"""
        _ = current_lang.translate
        if "__annotations__" not in self.locals:
            return

        hints = self.locals["__annotations__"]
        if not hints or hints == self.hints:
            return

        for name in hints:
            if name in self.hints and hints[name] == self.hints[name]:
                continue

            if name in dir(builtins):
                print(
                    _(
                        "Warning: you added a type hint to the python builtin '{name}'."
                    ).format(name=name)
                )
            elif (
                name not in self.locals
                or name in self.old_locals
                and self.old_locals[name] == self.locals[name]
            ):
                print(
                    _(
                        "Warning: you used type hints. Perhaps you meant {name} = {hint}."
                    ).format(name=name, hint=hints[name])
                )
        self.hints = copy.copy(hints)

    # The following two methods are never used in this class, but they are
    # defined in the parent class. The following are the equivalent methods
    # that can be used if an explicit call is desired for some reason.

    def showsyntaxerror(self, filename=None):
        public_api.explain()

    def showtraceback(self):
        public_api.explain()

    def raw_input(self, prompt=""):
        """Write a prompt and read a line.
        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.
        The base implementation uses the built-in function
        input(); a subclass may replace this with a different
        implementation.
        """
        if self.rich_console:
            return self.rich_console.input("[green]" + prompt)
        return input(prompt)


def start_console(local_vars=None, use_rich=False):
    """Starts a console; modified from code.interact"""
    console_defaults = {"friendly": public_api.Friendly()}
    public_api.install()

    if local_vars is None:
        local_vars = console_defaults
    else:
        local_vars.update(console_defaults)

    console = FriendlyConsole(locals=local_vars, use_rich=use_rich)
    console.interact(banner=BANNER)
