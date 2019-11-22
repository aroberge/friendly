import io
import linecache
import queue
import sys
import time
import traceback
import _thread as thread
import threading
import warnings

import tkinter  # Tcl, deletions, messagebox if startup fails

from idlelib import autocomplete  # AutoComplete, fetch_encodings
from idlelib import calltip  # Calltip
from idlelib import debugger_r  # start_debugger
from idlelib import debugobj_r  # remote_object_tree_item
from idlelib import iomenu  # encoding
from idlelib import rpc  # multiple objects
from idlelib import stackviewer  # StackTreeItem
from idlelib import __main__

import friendly_traceback

friendly_traceback.exclude_file_from_traceback(queue.__file__)
friendly_traceback.exclude_file_from_traceback(threading.__file__)
friendly_traceback.exclude_file_from_traceback(rpc.__file__)
friendly_traceback.exclude_file_from_traceback(__file__)
friendly_traceback.exclude_file_from_traceback(debugger_r.__file__)
import bdb

friendly_traceback.exclude_file_from_traceback(bdb.__file__)
del bdb

for mod in (
    "simpledialog",
    "messagebox",
    "font",
    "dialog",
    "filedialog",
    "commondialog",
    "ttk",
):
    delattr(tkinter, mod)
    del sys.modules["tkinter." + mod]

LOCALHOST = "127.0.0.1"


def idle_formatwarning(message, category, filename, lineno, line=None):
    """Format warnings the IDLE way."""

    s = "\nWarning (from warnings module):\n"
    s += '  File "%s", line %s\n' % (filename, lineno)
    if line is None:
        line = linecache.getline(filename, lineno)
    line = line.strip()
    if line:
        s += "    %s\n" % line
    s += "%s: %s\n" % (category.__name__, message)
    return s


def idle_showwarning_subproc(message, category, filename, lineno, file=None, line=None):
    """Show Idle-format warning after replacing warnings.showwarning.

    The only difference is the formatter called.
    """
    if file is None:
        file = sys.stderr
    try:
        file.write(idle_formatwarning(message, category, filename, lineno, line))
    except OSError:
        pass  # the file (probably stderr) is invalid - this warning gets lost.


_warnings_showwarning = None


def capture_warnings(capture):
    "Replace warning.showwarning with idle_showwarning_subproc, or reverse."

    global _warnings_showwarning
    if capture:
        if _warnings_showwarning is None:
            _warnings_showwarning = warnings.showwarning
            warnings.showwarning = idle_showwarning_subproc
    else:
        if _warnings_showwarning is not None:
            warnings.showwarning = _warnings_showwarning
            _warnings_showwarning = None


capture_warnings(True)
tcl = tkinter.Tcl()


def handle_tk_events(tcl=tcl):
    """Process any tk events that are ready to be dispatched if tkinter
    has been imported, a tcl interpreter has been created and tk has been
    loaded."""
    tcl.eval("update")


# Thread shared globals: Establish a queue between a subthread (which handles
# the socket) and the main thread (which runs user code), plus global
# completion, exit and interruptable (the main thread) flags:

exit_now = False
quitting = False
interruptable = False


def main(del_exitfunc=False):
    """Start the Python execution server in a subprocess

    In the Python subprocess, RPCServer is instantiated with handlerclass
    MyHandler, which inherits register/unregister methods from RPCHandler via
    the mix-in class SocketIO.

    When the RPCServer 'server' is instantiated, the TCPServer initialization
    creates an instance of run.MyHandler and calls its handle() method.
    handle() instantiates a run.Executive object, passing it a reference to the
    MyHandler object.  That reference is saved as attribute rpchandler of the
    Executive instance.  The Executive methods have access to the reference and
    can pass it on to entities that they command
    (e.g. debugger_r.Debugger.start_debugger()).  The latter, in turn, can
    call MyHandler(SocketIO) register/unregister methods via the reference to
    register and unregister themselves.

    """
    global exit_now
    global quitting
    global no_exitfunc
    no_exitfunc = del_exitfunc
    # time.sleep(15) # test subprocess not responding
    try:
        assert len(sys.argv) > 1
        port = int(sys.argv[-1])
    except Exception:
        print("IDLE Subprocess: no IP port passed in sys.argv.", file=sys.__stderr__)
        return

    capture_warnings(True)
    sys.argv[:] = [""]
    sockthread = threading.Thread(
        target=manage_socket, name="SockThread", args=((LOCALHOST, port),)
    )
    sockthread.daemon = True
    sockthread.start()
    while 1:
        try:
            if exit_now:
                try:
                    exit()
                except KeyboardInterrupt:
                    # exiting but got an extra KBI? Try again!
                    continue
            try:
                request = rpc.request_queue.get(block=True, timeout=0.05)
            except queue.Empty:
                request = None
                # Issue 32207: calling handle_tk_events here adds spurious
                # queue.Empty traceback to event handling exceptions.
            if request:
                seq, (method, args, kwargs) = request
                ret = method(*args, **kwargs)
                rpc.response_queue.put((seq, ret))
            else:
                handle_tk_events()
        except KeyboardInterrupt:
            if quitting:
                exit_now = True
            continue
        except SystemExit:
            capture_warnings(False)
            raise
        except Exception:
            # type, value, tb = sys.exc_info()
            try:
                print_exception()
                rpc.response_queue.put((seq, None))
            except Exception:
                # # Link didn't work, print same exception to __stderr__
                # traceback.print_exception(type, value, tb, file=sys.__stderr__)
                exit()
            else:
                continue


def manage_socket(address):
    for i in range(3):
        time.sleep(i)
        try:
            server = MyRPCServer(address, MyHandler)
            break
        except OSError as err:
            print(
                "IDLE Subprocess: OSError: " + err.args[1] + ", retrying....",
                file=sys.__stderr__,
            )
            socket_error = err
    else:
        print(
            "IDLE Subprocess: Connection to " "IDLE GUI failed, exiting.",
            file=sys.__stderr__,
        )
        show_socket_error(socket_error, address)
        global exit_now
        exit_now = True
        return
    server.handle_request()  # A single request only


def show_socket_error(err, address):
    "Display socket error from manage_socket."
    import tkinter
    from tkinter.messagebox import showerror

    root = tkinter.Tk()
    fix_scaling(root)
    root.withdraw()
    msg = (
        f"IDLE's subprocess can't connect to {address[0]}:{address[1]}.\n"
        f"Fatal OSError #{err.errno}: {err.strerror}.\n"
        f"See the 'Startup failure' section of the IDLE doc, online at\n"
        f"https://docs.python.org/3/library/idle.html#startup-failure"
    )
    showerror("IDLE Subprocess Error", msg, parent=root)
    root.destroy()


def print_exception():
    # flush_stdout()  # from Idle - leaving as reminder

    # Get a copy of stored code fragments from other process
    rpchandler = rpc.objecttable["exec"].rpchandler

    # Make sure the language is consistent
    current_lang = friendly_traceback.get_lang()
    try:
        requested_lang = rpchandler.remotecall(
            "friendly_traceback", "get_lang", tuple(), {}
        )
    except Exception:
        print("problem with get_lang remotecall")

    if requested_lang != current_lang:
        try:
            friendly_traceback.set_lang(requested_lang)
        except Exception:
            pass

    # Make sure that the verbosity level is consistent
    current_level = friendly_traceback.get_level()
    try:
        requested_level = rpchandler.remotecall(
            "friendly_traceback", "get_level", tuple(), {}
        )
    except Exception:
        print("problem with remotecall")
    if requested_level != current_level:
        friendly_traceback.set_level(current_level)

    # Ensure we have the right cache information
    friendly_cache = rpchandler.remotecall("cache", "get_copy", tuple(), {})
    # and update our local version with it
    for key in friendly_cache:
        friendly_traceback.cache.add(key, friendly_cache[key])

    # Finally, display the traceback
    friendly_traceback.explain()

    # Send a copy of our traceback info to the other process
    # in case a request to display it again is made
    # (by changing the verbosity level)
    try:
        rpchandler.remotecall(
            "friendly_traceback",
            "copy_traceback_info",
            (friendly_traceback.core.state.traceback_info,),
            {},
        )
    except Exception:
        print("problem with remotecall for copy traceback info")


# # The following function is kept so that unit tests still work.
# def cleanup_traceback(tb, exclude):
#     "Remove excluded traces from beginning/end of tb; get cached lines"
#     orig_tb = tb[:]
#     while tb:
#         for rpcfile in exclude:
#             if tb[0][0].count(rpcfile):
#                 break  # found an exclude, break for: and delete tb[0]
#         else:
#             break  # no excludes, have left RPC code, break while:
#         del tb[0]
#     while tb:
#         for rpcfile in exclude:
#             if tb[-1][0].count(rpcfile):
#                 break
#         else:
#             break
#         del tb[-1]
#     if len(tb) == 0:
#         # exception was in IDLE internals, don't prune!
#         tb[:] = orig_tb[:]
#         print("** IDLE Internal Exception: ", file=sys.stderr)
#     rpchandler = rpc.objecttable["exec"].rpchandler
#     for i in range(len(tb)):
#         fn, ln, nm, line = tb[i]
#         if nm == "?":
#             nm = "-toplevel-"
#         if not line and fn.startswith("<pyshell#"):
#             line = rpchandler.remotecall("linecache", "getline", (fn, ln), {})
#         tb[i] = fn, ln, nm, line


def flush_stdout():  # copied as is from Idle
    """XXX How to do this now?"""


def exit():
    """Exit subprocess, possibly after first clearing exit functions.

    If config-main.cfg/.def 'General' 'delete-exitfunc' is True, then any
    functions registered with atexit will be removed before exiting.
    (VPython support)

    """
    if no_exitfunc:
        import atexit

        atexit._clear()
    capture_warnings(False)
    sys.exit(0)


def fix_scaling(root):
    """Scale fonts on HiDPI displays."""
    import tkinter.font

    scaling = float(root.tk.call("tk", "scaling"))
    if scaling > 1.4:
        for name in tkinter.font.names(root):
            font = tkinter.font.Font(root=root, name=name, exists=True)
            size = int(font["size"])
            if size < 0:
                font["size"] = round(-0.75 * size)


class MyRPCServer(rpc.RPCServer):
    def handle_error(self, request, client_address):
        """Override RPCServer method for IDLE

        Interrupt the MainThread and exit server if link is dropped.

        """
        global quitting
        try:
            raise
        except SystemExit:
            raise
        except EOFError:
            global exit_now
            exit_now = True
            thread.interrupt_main()
        except Exception:
            erf = sys.__stderr__
            print("\n" + "-" * 40, file=erf)
            print("Unhandled server exception!", file=erf)
            print("Thread: %s" % threading.current_thread().name, file=erf)
            print("Client Address: ", client_address, file=erf)
            print("Request: ", repr(request), file=erf)
            traceback.print_exc(file=erf)
            print("\n*** Unrecoverable, server exiting!", file=erf)
            print("-" * 40, file=erf)
            quitting = True
            thread.interrupt_main()


# Pseudofiles for shell-remote communication (also used in pyshell)


class PseudoFile(io.TextIOBase):
    def __init__(self, shell, tags, encoding=None):
        self.shell = shell
        self.tags = tags
        self._encoding = encoding

    @property
    def encoding(self):
        return self._encoding

    @property
    def name(self):
        return "<%s>" % self.tags

    def isatty(self):
        return True


class PseudoOutputFile(PseudoFile):
    def writable(self):
        return True

    def write(self, s):
        if self.closed:
            raise ValueError("write to closed file")
        if type(s) is not str:
            if not isinstance(s, str):
                raise TypeError("must be str, not " + type(s).__name__)
            # See issue #19481
            s = str.__str__(s)
        return self.shell.write(s, self.tags)


class PseudoInputFile(PseudoFile):
    def __init__(self, shell, tags, encoding=None):
        PseudoFile.__init__(self, shell, tags, encoding)
        self._line_buffer = ""

    def readable(self):
        return True

    def read(self, size=-1):
        if self.closed:
            raise ValueError("read from closed file")
        if size is None:
            size = -1
        elif not isinstance(size, int):
            raise TypeError("must be int, not " + type(size).__name__)
        result = self._line_buffer
        self._line_buffer = ""
        if size < 0:
            while True:
                line = self.shell.readline()
                if not line:
                    break
                result += line
        else:
            while len(result) < size:
                line = self.shell.readline()
                if not line:
                    break
                result += line
            self._line_buffer = result[size:]
            result = result[:size]
        return result

    def readline(self, size=-1):
        if self.closed:
            raise ValueError("read from closed file")
        if size is None:
            size = -1
        elif not isinstance(size, int):
            raise TypeError("must be int, not " + type(size).__name__)
        line = self._line_buffer or self.shell.readline()
        if size < 0:
            size = len(line)
        eol = line.find("\n", 0, size)
        if eol >= 0:
            size = eol + 1
        self._line_buffer = line[size:]
        return line[:size]

    def close(self):
        self.shell.close()


class MyHandler(rpc.RPCHandler):
    def handle(self):
        """Override base method"""
        executive = Executive(self)
        self.register("exec", executive)
        self.console = self.get_remote_proxy("console")
        sys.stdin = PseudoInputFile(self.console, "stdin", iomenu.encoding)
        sys.stdout = PseudoOutputFile(self.console, "stdout", iomenu.encoding)
        sys.stderr = PseudoOutputFile(self.console, "stderr", iomenu.encoding)

        sys.displayhook = rpc.displayhook
        # page help() text to shell.
        import pydoc  # import must be done here to capture i/o binding

        pydoc.pager = pydoc.plainpager

        # Keep a reference to stdin so that it won't try to exit IDLE if
        # sys.stdin gets changed from within IDLE's shell. See issue17838.
        self._keep_stdin = sys.stdin

        self.interp = self.get_remote_proxy("interp")
        rpc.RPCHandler.getresponse(self, myseq=None, wait=0.05)

    def exithook(self):
        "override SocketIO method - wait for MainThread to shut us down"
        time.sleep(10)

    def EOFhook(self):
        "Override SocketIO method - terminate wait on callback and exit thread"
        global quitting
        quitting = True
        thread.interrupt_main()

    def decode_interrupthook(self):
        "interrupt awakened thread"
        global quitting
        quitting = True
        thread.interrupt_main()


init_code = """
import avantpy
"""


class Executive(object):
    def __init__(self, rpchandler):
        self.rpchandler = rpchandler
        self.locals = __main__.__dict__
        exec(init_code, self.locals)
        self.calltip = calltip.Calltip()
        self.autocomplete = autocomplete.AutoComplete()

    def runcode(self, code):
        global interruptable
        try:
            self.usr_exc_info = None
            interruptable = True
            try:
                exec(code, self.locals)
            finally:
                interruptable = False
        except SystemExit:
            # Scripts that raise SystemExit should just
            # return to the interactive prompt
            pass
        except Exception:
            # self.usr_exc_info = sys.exc_info()
            if quitting:
                exit()
            # even print a user code SystemExit exception, continue
            print_exception()
            jit = self.rpchandler.console.getvar("<<toggle-jit-stack-viewer>>")
            if jit:
                self.rpchandler.interp.open_remote_stack_viewer()
        else:
            flush_stdout()

    def interrupt_the_server(self):
        if interruptable:
            thread.interrupt_main()

    def start_the_debugger(self, gui_adap_oid):
        return debugger_r.start_debugger(self.rpchandler, gui_adap_oid)

    def stop_the_debugger(self, idb_adap_oid):
        "Unregister the Idb Adapter.  Link objects and Idb then subject to GC"
        self.rpchandler.unregister(idb_adap_oid)

    def get_the_calltip(self, name):
        return self.calltip.fetch_tip(name)

    def get_the_completion_list(self, what, mode):
        return self.autocomplete.fetch_completions(what, mode)

    def stackviewer(self, flist_oid=None):
        if self.usr_exc_info:
            typ, val, tb = self.usr_exc_info
        else:
            return None
        flist = None
        if flist_oid is not None:
            flist = self.rpchandler.get_remote_proxy(flist_oid)
        while tb and tb.tb_frame.f_globals["__name__"] in ["rpc", "run"]:
            tb = tb.tb_next
        sys.last_type = typ
        sys.last_value = val
        item = stackviewer.StackTreeItem(flist, tb)
        return debugobj_r.remote_object_tree_item(item)


capture_warnings(False)  # Make sure turned off; see issue 18081
