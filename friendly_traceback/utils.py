"""utils.py

A few useful objects which do not naturally fit anywhere else.
"""
import difflib

from . import debug_helper

import token_utils


def tokenize_source(source):
    """Makes a list of tokens from a source (str), ignoring space-like tokens
    and comments.
    """
    try:
        return token_utils.tokenize(source, warning=False)
    except Exception as e:
        debug_helper.log("Problem in token_utils.tokenize().")
        debug_helper.log(str(e))
        return []


def get_significant_tokens(source):
    """Gets a list of tokens from a source (str), ignoring comments
    as well as any token whose string value is either null or
    consists of spaces, newline or tab characters.
    """
    tokens = tokenize_source(source)
    return remove_meaningless_tokens(tokens)


def remove_meaningless_tokens(tokens):
    """Given a list of tokens, remove all space-like tokens and comments."""
    new_tokens = []
    for tok in tokens:
        if not tok.string.strip() or tok.is_comment():
            continue
        new_tokens.append(tok)
    return new_tokens


def get_comments(tokens):
    """Given a list of tokens, retrieves all the comment tokens
    returning a dict with the key equal to the line where the comment is
    found, and the item begin the comment token itself."""
    comments = {}
    for tok in tokens:
        if tok.is_comment():
            comments[tok.start_row] = tok
    return comments


# TODO: add unit test for this
def find_substring_index(main, substring):
    """Somewhat similar to the find() method for strings,
    this function determines if the tokens for substring appear
    as a subsequence of the tokens for main. If so, the index
    of the first token in returned, otherwise -1 is returned.
    """
    main_tokens = [tok.string for tok in get_significant_tokens(main)]
    sub_tokens = [tok.string for tok in get_significant_tokens(substring)]
    for index, token in enumerate(main_tokens):
        if (
            token == sub_tokens[0]
            and main_tokens[index : index + len(sub_tokens)] == sub_tokens
        ):
            return index
    return -1


def get_similar_words(word_with_typo, words):
    """Returns a list of similar words.

    The parameters we chose are based on experimenting with
    different values of the cutoff paramater for the difflib function
    get_close_matches.

    Suppose we have the following words:
    ['cos', 'cosh', 'acos', 'acosh']
    If we use a cutoff of 0.66, and ask for a maximum of 4 matches,
    all will be a match for 'cost'.  However, if we increase the cutoff
    to 0.67, 'acosh' will be dropped from the list, which seems sensible.

    However, this cutoff is "too generous" when dealing with long words.
    Using a cutoff up to 0.75 will result in both 'ascii_lowercase'
    and 'ascii_uppercase' matching 'ascii_lowecase'. Increasing the cutoff
    to 0.76 will drop ascii_uppercase as a match which also seems sensible.

    We thus use a heuristic cutoff based on length which ends up
    matching our expectation as to what a close match should be.

    We also do not return any matches for single character variables,
    nor do we consider single character variable potential matches.
    """
    if len(word_with_typo) == 1:
        return []
    words = [word for word in words if len(word) > 1]

    get = difflib.get_close_matches
    cutoff = min(0.8, 0.63 + 0.01 * len(word_with_typo))
    result = get(word_with_typo, words, n=5, cutoff=cutoff)
    if result:
        return result

    # The choice of parameters above might not be helpful in identifying
    # typos based on wrong case like 'Pi' or 'PI' instead of 'pi'.
    # In the absence of results, we try
    # to see if the typos could have been caused by using the wrong case
    result = get(word_with_typo.lower(), words, n=1, cutoff=cutoff)
    if result:
        return result
    else:
        result = get(word_with_typo.upper(), words, n=1, cutoff=cutoff)
    return result


def list_to_string(list_):
    """Transforms a list of names, like ['a', 'b', 'c'], into a single
    string of names, like "a, b, c"."""
    result = ["{c}".format(c=c.replace("'", "")) for c in list_]
    return ", ".join(result)
