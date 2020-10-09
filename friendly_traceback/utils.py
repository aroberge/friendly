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
        self.start = self.start_line, self.start_col = token[2]
        self.end = self.end_line, self.end_col = token[3]
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
    path_lower = path.lower()
    if path_lower.startswith(TESTS):
        path = "TESTS:" + path[len(TESTS) :]
    elif path_lower.startswith(FRIENDLY):
        path = "FRIENDLY:" + path[len(FRIENDLY) :]
    elif path_lower.startswith(PYTHON):
        path = "PYTHON:" + path[len(PYTHON) :]
    elif path_lower.startswith(HOME):
        path = "~" + path[len(HOME) :]
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


def edit_distance(word_with_typo, words):
    """Returns a list of similar words
    """
    similar_words = difflib.get_close_matches(word_with_typo, words, cutoff=0.7)
    return [word for word in similar_words if word != "_"]
