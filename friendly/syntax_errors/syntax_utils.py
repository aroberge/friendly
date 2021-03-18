"""This file contains various functions used for analysis of SyntaxErrors"""

from ..my_gettext import current_lang


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
    names = {
        "(": _("parenthesis `(`"),
        ")": _("parenthesis `)`"),
        "[": _("square bracket `[`"),
        "]": _("square bracket `]`"),
        "{": _("curly bracket `{`"),
        "}": _("curly bracket `}`"),
    }
    return names[str(bracket)]  # bracket could be a Token or a str
