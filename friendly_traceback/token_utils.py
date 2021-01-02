"""token_utils.py
------------------

A collection of useful functions and methods to deal with tokenizing
source code.
"""
import ast
import keyword
import tokenize as py_tokenize

from io import StringIO

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
    automatically obtain a transformed source. Almost always, the attribute
    to be transformed will be the string attribute.
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

    def __str__(self):
        """Returns the string attribute."""
        return self.string

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

    def is_name(self):
        """Returns ``True`` if the token is a type NAME"""
        return self.type == py_tokenize.NAME

    def is_keyword(self):
        """Returns True if the token represents a Python keyword."""
        return keyword.iskeyword(self.string)

    def is_number(self):
        """Returns True if the token represents a number"""
        return self.type == py_tokenize.NUMBER

    def is_float(self):
        """Returns True if the token represents a float"""
        return self.is_number() and isinstance(ast.literal_eval(self.string), float)

    def is_integer(self):
        """Returns True if the token represents an integer"""
        return self.is_number() and isinstance(ast.literal_eval(self.string), int)

    def is_complex(self):
        """Returns True if the token represents a complex number"""
        return self.is_number() and isinstance(ast.literal_eval(self.string), complex)

    def is_space(self):
        """Returns True if the token indicates a change in indentation,
        the end of a line, or the end of the source
        (``INDENT``, ``DEDENT``, ``NEWLINE``, ``NL``, and ``ENDMARKER``).

        Note that spaces, including tab characters ``\\t``, between tokens
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

    def is_in(self, iterable):
        """Returns True if the string attribute is found as an item of iterable."""
        return self.string in iterable

    def is_not_in(self, iterable):
        """Returns True if the string attribute is found as an item of iterable."""
        return self.string not in iterable

    def immediately_before(self, other):
        """Return True if other self is immediately before other,
        without any intervening space in between the two tokens.
        """
        return self.end_row == other.start_row and self.end_col == other.start_col


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


def fix_empty_line(source, tokens):
    """Python's tokenizer drops entirely a last line if it consists only of
    space characters and/or tab characters.  To ensure that we can always have::

        untokenize(tokenize(source)) == source

    we correct the last token content if needed.
    """
    nb = 0
    for char in reversed(source):
        if char in (" ", "\t"):
            nb += 1
        else:
            break
    tokens[-1].string = source[-nb:]


def tokenize(source):
    """Transforms a source (string) into a list of Tokens.

    If an exception is raised by Python's tokenize module, the list of tokens
    accumulated up to that point is returned.
    """
    tokens = []

    try:
        for tok in py_tokenize.generate_tokens(StringIO(source).readline):
            token = Token(tok)
            tokens.append(token)
    except (py_tokenize.TokenError, Exception):
        return tokens

    if source.endswith((" ", "\t")):
        fix_empty_line(source, tokens)

    return tokens


def get_lines(source):
    """Transforms a source (string) into a list of Tokens, with each
    (inner) list containing all the tokens found on a given line of code.
    """
    lines = []
    current_row = -1
    new_line = []
    try:
        for tok in py_tokenize.generate_tokens(StringIO(source).readline):
            token = Token(tok)
            if token.start_row != current_row:
                current_row = token.start_row
                if new_line:
                    lines.append(new_line)
                new_line = []
            new_line.append(token)
        if new_line:
            lines.append(new_line)
    except (py_tokenize.TokenError, Exception):
        return lines

    if source.endswith((" ", "\t")):
        fix_empty_line(source, lines[-1])
    return lines


def strip_comment(line):
    """Removes comments from a line"""
    tokens = []
    try:
        for tok in py_tokenize.generate_tokens(StringIO(line).readline):
            token = Token(tok)
            if token.is_comment():
                continue
            tokens.append(token)
    except py_tokenize.TokenError:
        pass
    return untokenize(tokens)


def dedent(tokens, nb):
    """Given a list of tokens, produces an equivalent list corresponding
    to a line of code with the first nb characters removed.
    """
    line = untokenize(tokens)
    line = line[nb:]
    return tokenize(line)


def indent(tokens, nb, tab=False):
    """Given a list of tokens, produces an equivalent list corresponding
    to a line of code with nb space characters inserted at the beginning.

    If ``tab`` is specified to be ``True``, ``nb`` tab characters are inserted
    instead of spaces.
    """
    line = untokenize(tokens)
    if tab:
        line = "\t" * nb + line
    else:
        line = " " * nb + line
    return tokenize(line)


def untokenize(tokens):
    """Return source code based on tokens.

    Adapted from https://github.com/myint/untokenize,
    Copyright (C) 2013-2018 Steven Myint, MIT License (same as this project).

    This is similar to Python's own tokenize.untokenize(), except that it
    preserves spacing between tokens, by using the line
    information recorded by Python's tokenize.generate_tokens.
    As a result, if the original source code had multiple spaces between
    some tokens or if escaped newlines were used or if tab characters
    were present in the original source, those will also be present
    in the source code produced by untokenize.

    Thus ``source == untokenize(tokenize(source))``.

    Note: if you you modifying tokens from an original source:

    Instead of full token object, ``untokenize`` will accept simple
    strings; however, it will only insert them *as is* without taking them
    into account when it comes with figuring out spacing between tokens.
    """
    words = []
    previous_line = ""
    last_row = 0
    last_column = -1
    last_non_whitespace_token_type = None

    for token in tokens:
        if isinstance(token, str):
            words.append(token)
            continue
        if token.type == py_tokenize.ENCODING:
            continue

        # Preserve escaped newlines.
        if (
            last_non_whitespace_token_type != py_tokenize.COMMENT
            and token.start_row > last_row
        ):
            if previous_line.endswith(("\\\n", "\\\r\n", "\\\r")):
                words.append(previous_line[len(previous_line.rstrip(" \t\n\r\\")) :])

        # Preserve spacing.
        if token.start_row > last_row:
            last_column = 0
        if token.start_col > last_column:
            words.append(token.line[last_column : token.start_col])

        words.append(token.string)

        previous_line = token.line
        last_row = token.end_row
        last_column = token.end_col
        if not token.is_space():
            last_non_whitespace_token_type = token.type

    return "".join(words)


def print_tokens(source):
    """Prints tokens found in source, excluding spaces and comments.

    ``source`` is either a string to be tokenized, or a list of Token objects.

    This is occasionally useful as a debugging tool.
    """
    if isinstance(source[0], Token):
        source = untokenize(source)

    for lines in get_lines(source):
        for token in lines:
            print(repr(token))
        print()
