"""analyze_syntax.py

Collection of functions useful attempting to determine the
cause of a SyntaxError and providing a somewhat detailed explanation.

In an ideal world, one would write a custom parser for Python, extending
the existing one with enhanced error messages about where in the parsing
process a SyntaxError occurred, what kind of token was expected, etc.,
and use that information to give feedback to users.

Unfortunately, we do not live in such a world.

Friendly-traceback uses some ad-hoc heuristics to analyze the information
given by Python or the code itself and makes an attempt at guessing
as often as possible what went wrong while trying to avoid giving
incorrect information.
"""

from friendly_traceback.my_gettext import current_lang, internal_error
from . import statement_analyzer
from . import message_analyzer
from .. import debug_helper


def unknown_cause():
    _ = current_lang.translate
    return _(
        "Currently, I cannot guess the likely cause of this error.\n"
        "Try to examine closely the line indicated as well as the line\n"
        "immediately above to see if you can identify some misspelled\n"
        "word, or missing symbols, like (, ), [, ], :, etc.\n"
        "\n"
        "Unless your code uses type annotations, which are beyond our scope,\n"
        "if you think that this is something which should be handled\n"
        "by Friendly-traceback, please report this case to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
        "\n"
    )


def set_cause_syntax(value, tb_data):
    """Gets the likely cause of a given exception based on some information
    specific to a given exception.
    """
    _ = current_lang.translate
    try:
        return find_syntax_error_cause(value, tb_data)
    except Exception as e:
        debug_helper.log_error(e)
        return {"cause": internal_error()}


def find_syntax_error_cause(value, tb_data):
    """Attempts to find the cause of a SyntaxError"""
    # value = tb_data.value
    _ = current_lang.translate
    message = value.msg
    statement = tb_data.statement

    # If Python includes a descriptive enough message, we rely
    # on the information that it provides. We know that sometimes
    # this might give the wrong diagnostic but one of our objectives
    # is to explain in simpler language what Python means when it
    # raises a particular exception.

    if "invalid syntax" not in message:
        cause = message_analyzer.analyze_message(message=message, statement=statement)
        if cause:
            return cause
        else:
            cause = statement_analyzer.analyze_statement(statement)
            if not cause:
                return {"cause": unknown_cause()}
            notice = _(
                "Python gave us the following informative message\n"
                "about the possible cause of the error:\n\n"
                "    {message}\n\n"
                "However, I do not recognize this information and I have\n"
                "to guess what caused the problem, but I might be wrong.\n\n"
            ).format(message=message)
            cause["cause"] = notice + cause["cause"]
            return cause
    else:
        cause = statement_analyzer.analyze_statement(statement)
        if cause:
            return cause

    return {"cause": unknown_cause()}
