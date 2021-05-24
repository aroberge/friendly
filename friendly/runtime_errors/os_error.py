"""Only identifying failed connection to a server for now."""
from ..my_gettext import current_lang, no_information


def get_cause(_value, _frame, tb_data):

    tb = "\n".join(tb_data.formatted_tb)
    if (
        "socket.gaierror" in tb
        or "urllib.error" in tb
        or "urllib3.exception" in tb
        or "requests.exception" in tb
    ):
        return handle_connection_error()
    return no_information()


def handle_connection_error():
    _ = current_lang.translate
    cause = _(
        "I suspect that you are trying to connect to a server and\n"
        "that a connection cannot be made.\n\n"
        "If that is the case, check for typos in the URL\n"
        "and check your internet connectivity.\n"
    )
    return {"cause": cause}
