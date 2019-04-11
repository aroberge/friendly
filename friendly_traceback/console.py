"""console.py

Adaptation of Python's console found in code.py
as well as from
https://github.com/Qix-/better-exceptions/blob/master/better_exceptions/repl.py

"""

# The code below could be simplified if we used super().some_method(...)
# in a few places. However, this would put the onus of anyone wanting
# to modify this code to also refer to the `code` module in the standard
# library.

import os
import platform
import sys

from code import InteractiveConsole

from .core import state
from .version import __version__
from . import utils


class FriendlyConsole(InteractiveConsole):
    def __init__(self, locals=None):
        super().__init__(locals=locals)
        self.true_filename_plus_source = None
        self.fake_filename = None
        self.counter = 0

    def runsource(self, source, filename="<input>", symbol="single"):
        """Compile and run some source in the interpreter.

        Arguments are as for compile_command().

        One several things can happen:

        1) The input is incorrect; compile_command() raised an
        exception (SyntaxError or OverflowError).  A syntax traceback
        will be printed by calling the showsyntaxerror() method.

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
        self.true_filename_plus_source = ("<console>", source)
        self.filename = self.fake_filename = filename = "<console:%d>" % self.counter
        utils.add_console_source(self.fake_filename, self.true_filename_plus_source)
        self.counter += 1
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            return False

        if code is None:
            # Case 2
            return True

        # Case 3
        self.runcode(code)
        return False

    def runcode(self, code):
        """Execute a code object.

        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which, unlike the case for the original version in the
        standard library, cleanly exists the program. This is done
        so as to avoid our Friendly-traceback's exception hook to intercept
        it and confuse the users.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.

        """
        utils.add_console_source(self.fake_filename, self.true_filename_plus_source)
        try:
            exec(code, self.locals)
        except SystemExit:
            os._exit(1)
        except Exception:
            self.showtraceback()

    def showsyntaxerror(self, filename=None):
        """Display the syntax error that just occurred.

        This doesn't display a stack trace because there isn't one.

        If a filename is given, it is stuffed in the exception instead
        of what was there before (because Python's parser always uses
        "<string>" when reading from a string).
        """
        try:
            type, value, tb = sys.exc_info()
            sys.last_type = type
            sys.last_value = value
            sys.last_traceback = tb
            if filename and type is SyntaxError:
                # Work hard to stuff the correct filename in the exception
                try:
                    msg, (dummy_filename, lineno, offset, line) = value.args
                except ValueError:
                    # Not the format we expect; leave it alone
                    pass
                else:
                    # Stuff in the right filename
                    value = SyntaxError(msg, (filename, lineno, offset, line))
                    sys.last_value = value
            sys.excepthook(type, value, tb)
        finally:
            del tb

    def showtraceback(self):
        """Display the exception that just occurred.

        We remove the first stack item because it is our own code.
        """
        sys.last_type, sys.last_value, last_tb = ei = sys.exc_info()
        sys.last_traceback = last_tb
        try:
            sys.excepthook(ei[0], ei[1], last_tb.tb_next)
        finally:
            last_tb = ei = None


def start_console(local_vars=None, show_python=False):
    """Starts a console; modified from code.interact"""
    console_defaults = {"set_lang": state.install_gettext}

    if local_vars is None:
        local_vars = console_defaults
    else:
        local_vars.update(console_defaults)

    console = FriendlyConsole(locals=local_vars)

    banner = "{} version {}. [Python version: {}]\n".format(
        utils.CONSOLE_NAME, __version__, platform.python_version()
    )
    console.interact(banner=banner)
