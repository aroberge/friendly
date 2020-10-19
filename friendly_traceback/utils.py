"""utils.py

A few useful objects which do not naturally fit anywhere else.
"""
import difflib
import token as token_module
import tokenize
import os.path

from io import StringIO

from .friendly_exception import FriendlyException


_token_format = "{type:<10}{string:<25} {start:^12} {end:^12} {line:^12}"


class Token:
    """Token as generated from tokenize.generate_tokens written here in
    a more convenient form for our purpose.
    """

    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start = self.start_row, self.start_col = token[2]
        self.end = self.end_row, self.end_col = token[3]
        self.line = token[4]
        if self.line and self.line[-1] == "\n":
            self.line = self.line[:-1]

    def __repr__(self):
        return _token_format.format(
            type=token_module.tok_name[self.type],
            string=self.string,
            start=str(self.start),
            end=str(self.end),
            line=str(self.line),
        )


def tokenize_source(source):
    """Makes a list of tokens from a source (str), ignoring spaces and comments."""
    tokens = []
    try:
        for tok in tokenize.generate_tokens(StringIO(source).readline):
            token = Token(tok)
            if not token.string.strip():  # ignore spaces
                continue
            if token.type == tokenize.COMMENT:
                break
            tokens.append(token)
    except tokenize.TokenError:
        return tokens
    except Exception as e:
        raise FriendlyException("%s --> utils.tokenize_source" % repr(e))

    return tokens


def tokenize_source_lines(source_lines):
    """Makes a list of tokens from a source (list of lines),
    ignoring spaces and comments.
    """
    source = "\n".join(source_lines)
    return tokenize_source(source)


PYTHON = os.path.dirname(tokenize.__file__).lower()
this_dir = os.path.dirname(__file__)
FRIENDLY = os.path.abspath(os.path.join(this_dir, "..")).lower()
TESTS = os.path.join(FRIENDLY, "tests").lower()
HOME = os.path.expanduser("~").lower()


def shorten_path(path):
    # On windows, the filenames are not case sensitive
    # and the way Python displays filenames may vary.
    # To properly compare, we convert everything to lowercase
    # However, we ensure that the shortened path retains its cases
    path = path.replace("'", "")  # We might get passed a path repr
    path = os.path.normpath(path)
    path_lower = path.lower()
    if path_lower.startswith(TESTS):
        path = "TESTS:" + path[len(TESTS) :]
    elif path_lower.startswith(FRIENDLY):
        path = "FRIENDLY:" + path[len(FRIENDLY) :]
    elif path_lower.startswith(PYTHON):
        path = "PYTHON_LIB:" + path[len(PYTHON) :]
    elif path_lower.startswith(HOME):
        path = "HOME_DIR:" + path[len(HOME) :]
    return path


def make_token_table(source):
    """Prints tokens found in source, excluding spaces and comments.

    This was useful and might agin be useful to use
    when writing new exception analyzers.
    """
    print(
        _token_format.format(
            type="Type", string="String", start="Start", end="End", line="last"
        )
    )
    print("-" * 73)
    tokens = tokenize_source(source)
    for token in tokens:
        print(token)


def get_similar_words(word_with_typo, words):
    """Returns a list of similar words"""
    # The parameters we chose are based on experimenting with
    # different values of the cutoff paramater for the difflib function
    # get_close_matches.
    #
    # Suppose we have the following words:
    # ['cos', 'cosh', 'acos', 'acosh']
    # If we use a cutoff of 0.66, and ask for a maximum of 4 matches,
    # all will be a match for 'cost'.  However, if we increase the cutoff
    # to 0.67, 'acosh' will be dropped from the list, which seems sensible.
    #
    # However, this cutoff is "too generous" when dealing with long words.
    # Using a cutoff up to 0.75 will result in both 'ascii_lowercase'
    # and 'ascii_uppercase' matching 'ascii_lowecase'. Increasing the cutoff
    # to 0.76 will drop ascii_uppercase as a match which also seems sensible.
    #
    # We thus use a heuristic cutoff based on length which ends up
    # matching our expectation as to what a close match should be.
    get = difflib.get_close_matches

    cutoff = min(0.8, 0.65 + 0.01 * len(word_with_typo))
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
