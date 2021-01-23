"""This file contains various functions used for analysis of SyntaxErrors"""

from .. import debug_helper
from ..my_gettext import current_lang

from .. import token_utils


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


# TODO: remove this and use fixers' version instead
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
        debug_helper.log("Problem in token_utils.modify_source().")
        debug_helper.log("Empty token list was received")
        debug_helper.log_error()
        return ""

    try:
        new_tokens = []
        original_string = bad_token.string
        for tok in tokens:
            if tok is bad_token:
                if add:
                    tok.string += string
                else:
                    tok.string = string
            new_tokens.append(tok)

        source = token_utils.untokenize(new_tokens)
        bad_token.string = original_string
        if tokens[0].start_row == tokens[-1].start_row:
            return source.strip()
        else:
            return source
    except Exception as e:
        debug_helper.log("Problem in token_utils.modify_source().")
        debug_helper.log_error(e)
        return ""
