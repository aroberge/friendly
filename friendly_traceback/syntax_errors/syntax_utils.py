"""This file contains various functions used for analysis of SyntaxErrors"""

from .. import debug_helper
from ..my_gettext import current_lang

import token_utils


def count_char(tokens, char):
    """Counts how many times a given character appears in a list of tokens"""
    return sum(1 for token in tokens if token == char)


def no_unclosed_brackets(tokens):
    """Returns True if the number of opening bracket of types (, [, and {,
    match their closing counterpart.
    """

    return (
        (count_char(tokens, "(") == count_char(tokens, ")"))
        and (count_char(tokens, "[") == count_char(tokens, "]"))
        and (count_char(tokens, "{") == count_char(tokens, "}"))
    )


def matching_brackets(bra, ket):
    return (
        (bra == "(" and ket == ")")
        or (bra == "[" and ket == "]")
        or (bra == "{" and ket == "}")
    )


def name_bracket(bracket):
    _ = current_lang.translate
    if bracket == "(":
        return _("parenthesis `(`")
    elif bracket == ")":
        return _("parenthesis `)`")
    elif bracket == "[":
        return _("square bracket `[`")
    elif bracket == "]":
        return _("square bracket `]`")
    elif bracket == "{":
        return _("curly bracket `{`")
    else:
        return _("curly bracket `}`")


def modify_source(tokens, bad_token, string, add=False):
    """Replaces a single token string to produce a new source.
    More specifically, given::

        tokens: a list of tokens
        bad_token: single token to be replaced
        string: new string to use
        add: if True, the new string is added to the existing one

    It creates a new list of token with the replacement having been done,
    untokenize it to produce a modified source.

    If the original tokens were on a single line, the source is stripped
    of any spaces
    """
    if not tokens:
        debug_helper.log("Problem in token_utils.modify_source().")
        debug_helper.log("Empty token list was received")
        return ""

    try:
        new_tokens = []
        for tok in tokens:
            if tok == bad_token:
                if add:
                    tok.string += string
                else:
                    tok.string = string
            new_tokens.append(tok)

        source = token_utils.untokenize(new_tokens)
        if tokens[0].start_row == tokens[-1].start_row:
            return source.strip()
        else:
            return source
    except Exception as e:
        debug_helper.log("Problem in token_utils.modify_source().")
        debug_helper.log(str(e))
        return ""


def check_statement(statement):
    """Given a single line of code expected to be a valid 'statement',
    that is a line which could be part of a larger source of code and
    contains no unmatched brackets and would not end with the continuation
    character, it is potentially modified to include some required
    'environment' and compiled to see if it raises any SyntaxErrors.

    Returns True if no SyntaxError is raised, False otherwise.
    """
    try:
        statement = statement.strip()
        if statement.endswith(":"):
            statement += " pass"

        if statement.startswith("elif") or statement.startswith("else"):
            statement = if_block % statement
        elif statement.startswith("return") or statement.startswith("yield"):
            statement = def_block % statement
        elif statement.startswith("except") or statement.startswith("finally"):
            statement = try_block % statement

        try:
            compile(statement, "fake-file", "exec")
            return True
        except SyntaxError:
            return False

    except Exception as e:
        debug_helper.log("Problem in token_utils.check_statement().")
        debug_helper.log(str(e))
        return False


if_block = """
if True:
    pass
%s
"""

def_block = """
def test():
    %s
"""

try_block = """
try:
    pass
%s
"""
