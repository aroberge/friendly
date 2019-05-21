"""console.py

Adaptation of Python's console found in code.py so that it can be
used to show some "friendly" tracebacks.
"""

import os
import platform

from code import InteractiveConsole

from . import public_api
from .source_cache import cache
from .path_info import exclude_file_from_traceback

from .version import __version__


class FriendlyConsole(InteractiveConsole):
    def __init__(self, locals=None):

        import codeop  # called by Python's code module and would otherwise

        exclude_file_from_traceback(codeop.__file__)  # appear in tracebacks

        super().__init__(locals=locals)
        self.fake_filename = None
        self.counter = 0

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
        filename = "<friendly-console:%d>" % self.counter
        cache.add(filename, source)
        self.counter += 1
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
        try:
            exec(code, self.locals)
        except SystemExit:
            os._exit(1)
        except Exception:
            public_api.explain()

    # Since we exclude files in this package from being included in the
    # tracebacks, we do not need to do any special handling to remove
    # a frame from the tracebacks as is done in Python's
    # code.InteractiveConsole. Thus, we have no need for the following
    # two methods, but define them in case subclasses accidently called
    # them.

    def showsyntaxerror(self, filename=None):
        public_api.explain()

    def showtraceback(self):
        public_api.explain()


def start_console(local_vars=None, show_python=False):
    """Starts a console; modified from code.interact"""
    console_defaults = {
        "set_lang": public_api.set_lang,
        "set_level": public_api.set_level,
    }

    if local_vars is None:
        local_vars = console_defaults
    else:
        local_vars.update(console_defaults)

    console = FriendlyConsole(locals=local_vars)

    banner = "{} version {}. [Python version: {}]\n".format(
        "Friendly Console", __version__, platform.python_version()
    )
    console.interact(banner=banner)
