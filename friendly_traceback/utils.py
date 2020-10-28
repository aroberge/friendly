"""utils.py

A few useful objects which do not naturally fit anywhere else.
"""
import difflib
import keyword
import tokenize as py_tokenize
import os.path

from io import StringIO

from .friendly_exception import FriendlyException

_token_format = "type={type}  string={string}  start={start}  end={end}  line={line}"


class Token:
    """Token as generated from Python's tokenize.generate_tokens written here in
    a more convenient form, and with some custom methods.

    The various parameters are::

        type: token type
        string: the token written as a string
        start = (start_row, start_col)
        end = (end_row, end_col)
        line: entire line of code where the token is found.

    Token instances are mutable objects. Therefore, given a list of tokens,
    we can change the value of any token's attribute, untokenize the list and
    automatically obtain a transformed source.
    """

    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start = self.start_row, self.start_col = token[2]
        self.end = self.end_row, self.end_col = token[3]
        self.line = token[4]

    def __eq__(self, other):
        """Compares a Token with another object; returns true if
        self.string == other.string or if self.string == other.
        """
        if hasattr(other, "string"):
            return self.string == other.string
        elif isinstance(other, str):
            return self.string == other
        else:
            raise TypeError(
                "A token can only be compared to another token or to a string."
            )

    def is_comment(self):
        """Returns True if the token is a comment."""
        return self.type == py_tokenize.COMMENT

    def is_identifier(self):
        """Returns ``True`` if the token represents a valid Python identifier
        excluding Python keywords.

        Note: this is different from Python's string method ``isidentifier``
        which also returns ``True`` if the string is a keyword.
        """
        return self.string.isidentifier() and not self.is_keyword()

    def is_integer(self):
        """Returns True if the token represents an integer"""
        return self.is_number() and self.string.isdigit()

    def is_keyword(self):
        """Returns True if the token represents a Python keyword."""
        return keyword.iskeyword(self.string)

    def is_number(self):
        """Returns True if the token represents a number"""
        return self.type == py_tokenize.NUMBER

    def is_space(self):
        """Returns True if the token indicates a change in indentation,
        the end of a line, or the end of the source
        (``INDENT``, ``DEDENT``, ``NEWLINE``, ``NL``, and ``ENDMARKER``).

        Note that spaces, including tab charcters ``\\t``, between tokens
        on a given line are not considered to be tokens themselves.
        """
        return self.type in (
            py_tokenize.INDENT,
            py_tokenize.DEDENT,
            py_tokenize.NEWLINE,
            py_tokenize.NL,
            py_tokenize.ENDMARKER,
        )

    def is_string(self):
        """Returns True if the token is a string"""
        return self.type == py_tokenize.STRING

    def __repr__(self):
        """Nicely formatted token to help with debugging session.

        Note that it does **not** print a string representation that could be
        used to create a new ``Token`` instance, which is something you should
        never need to do other than indirectly by using the functions
        provided in this module.
        """
        return _token_format.format(
            type="%s (%s)" % (self.type, py_tokenize.tok_name[self.type]),
            string=repr(self.string),
            start=str(self.start),
            end=str(self.end),
            line=repr(self.line),
        )


def find_token_by_position(tokens, row, column):
    """Given a list of tokens, a specific row (linenumber) and column,
    a two-tuple is returned that includes the token
    found at that position as well as its list index.

    If no such token can be found, ``None, None`` is returned.
    """
    for index, tok in enumerate(tokens):
        if (
            tok.start_row <= row <= tok.end_row
            and tok.start_col <= column < tok.end_col
        ):
            return tok, index
    return None, None


def get_significant_tokens(source):
    """Gets a list of tokens from a source (str), ignoring comments
    as well as any token whose string value is either null or
    consists of spaces, newline or tab characters.

    If an exception is raised by Python's tokenize module, the list of tokens
    accumulated up to that point is returned.
    """
    tokens = []
    try:
        for tok in py_tokenize.generate_tokens(StringIO(source).readline):
            token = Token(tok)
            if not token.string.strip():
                continue
            if token.is_comment():
                continue
            tokens.append(token)
    except py_tokenize.TokenError:
        return tokens

    return tokens


def tokenize_source(source):
    """Makes a list of tokens from a source (str), ignoring space-like tokens
    and comments.
    """
    try:
        return get_significant_tokens(source)
    except Exception as e:
        raise FriendlyException("%s --> utils.tokenize_source" % repr(e))


def tokenize_source_lines(source_lines):
    """Makes a list of tokens from a source (list of lines),
    ignoring spaces and comments.
    """
    source = "\n".join(source_lines)
    return tokenize_source(source)


PYTHON = os.path.dirname(py_tokenize.__file__).lower()
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
