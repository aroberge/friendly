"""First implementation"""

import sys

from ..my_gettext import current_lang, no_information


def get_cause(exception):

    if "socket" in sys.modules:
        import socket

        socket_error = socket.error
    else:
        socket_error = None

    if issubclass(exception, OSError):
        if "socket" in sys.modules and issubclass(exception, socket_error):
            return handle_connection_error()
        elif issubclass(exception, ConnectionError):
            return handle_connection_error()
        else:
            return no_information()


def handle_connection_error():
    _ = current_lang.translate
    return _(
        "I suspect that you are trying to connect to a server and\n"
        "that a connection cannot be made.\n\n"
        "If that is the case, check for typos in the URL\n"
        "and check your internet connectivity.\n"
    )
