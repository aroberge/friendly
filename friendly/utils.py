"""utils.py

A few useful objects which do not naturally fit anywhere else.
"""
import difflib


def get_similar_words(word_with_typo, words):
    """Returns a list of similar words.

    The parameters we chose are based on experimenting with
    different values of the cutoff parameter for the difflib function
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


def list_to_string(list_, sep=", "):
    """Transforms a list of names, like ['a', 'b', 'c'], into a single
    string of names, like "a, b, c"."""
    result = ["{c}".format(c=c.replace("'", "")) for c in list_]
    return sep.join(result)
