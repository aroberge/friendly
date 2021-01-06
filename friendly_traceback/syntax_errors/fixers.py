"""Various functions used to find fixes to SyntaxErrors"""

from .. import debug_helper
from .. import token_utils


def modify_source(tokens, bad_token, string, add=False):
    """Replaces a single token string to produce a new source.
    More specifically, given::

        tokens: a list of tokens
        bad_token: single token to be replaced
        string: new string to use
        add: if True, the new string is added to the existing one

    It creates a new list of tokens with the replacement having been done,
    untokenize it to produce a modified source which is stripped of
    leading and ending spaces so that it could be inserted in a
    code sample at the beginning of a line with no indentation.
    """
    if not tokens:
        debug_helper.log("Problem in fixers.modify_source().")
        debug_helper.log("Empty token list was received")
        debug_helper.log_error()
        return ""

    try:
        new_tokens = []
        for tok in tokens:
            if tok is bad_token:
                new_token = bad_token.copy()
                if add:
                    new_token.string += string
                else:
                    new_token.string = string
                new_tokens.append(new_token)
            else:
                new_tokens.append(tok)

        source = token_utils.untokenize(new_tokens)
        return source.strip()
    except Exception as e:
        debug_helper.log("Problem in fixers.modify_source().")
        debug_helper.log_error(e)
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
        debug_helper.log_error(e)
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
