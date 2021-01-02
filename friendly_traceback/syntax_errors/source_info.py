"""Contains a class that compiles and stores all the information that
is relevant to the analysis of SyntaxErrors.
"""

from ..source_cache import cache
from .syntax_utils import matching_brackets
from .. import debug_helper
from .. import token_utils


class Statement:
    """Instances of this class contain all relevant information required
    for the various functions that attempt to determine the cause of
    SyntaxError.

    The basic idea is to retrieve a "complete statement" where the
    exception is raised. By "complete statement", we mean the smallest
    number of consecutive lines of code that contains the line where
    the exception was raised and includes matching pairs of brackets,
    (), [], {}. If a problem arises due to non-matching pairs of brackets,
    this information is available (variables begin_brackets or end_bracket).

    A complete statement is saved as a list of tokens (statement_tokens)
    from which it could be reconstructed using an untokenize function.

    From this list of tokens, a secondary list is obtained (tokens) by
    removing all space-like and comment tokens, which are the only
    meaningful tokens needed to do the analysis.

    To simplify the code doing the error analysis itself, we precompute various
    parameters (e.g. does the statement fits on a single line, how many
    meaningful tokens are included, what are the first and last tokens
    on that statement, etc.) which are needed for some functions.
    """

    def __init__(self, value, tb_data):
        self.linenumber = value.lineno
        self.message = value.msg
        self.filename = value.filename
        self.bad_line = tb_data.bad_line  # previously obtained from the traceback

        self.fstring_error = self.filename == "<fstring>" or "f-string" in self.message

        self.all_statement_tokens = []  # include newlines, comments, etc.
        self.tokens = []  # meaningful tokens
        self.begin_brackets = []
        self.end_bracket = None
        self.bad_token = None
        self.prev_token = None  # meaningful token preceding bad token
        self.next_token = None  # meaningful token following bad token
        self.bad_token_index = 0
        self.first_token = None
        self.last_token = None
        self.single_line = True

        if self.linenumber is not None:
            source_tokens = self.get_source_tokens(value)
            self.obtain_statement(source_tokens, value.offset)
            self.tokens = self.remove_meaningless_tokens()
        elif "too many statically nested blocks" not in self.message:
            debug_helper.log("linenumber is None in analyze_syntax._find_likely_cause")

        self.nb_tokens = len(self.tokens)
        self.is_complete = not (self.begin_brackets or self.end_bracket)
        if self.nb_tokens >= 1:
            self.first_token = self.tokens[0]
            self.last_token = self.tokens[-1]
            self.single_line = (
                self.first_token.start_row == self.last_token.end_row
                and self.is_complete
            )

        if self.bad_token is not None:  # this should always be ok
            try:
                self.next_token = self.tokens[self.bad_token_index + 1]
            except Exception:
                self.next_token = None

    def get_source_tokens(self, value):
        """Returns a list containing all the tokens from the source."""
        source_lines = cache.get_source_lines(value.filename)
        source = "".join(source_lines)
        if not source.strip():
            source = self.bad_line or "\n"
        return token_utils.tokenize(source)

    def obtain_statement(self, source_tokens, offset):
        """This method scans the source searching for the statement that
        caused the problem. Most often, it will be a single line of code.
        However, it might occasionally be a multiline statement that
        includes code surrounded by some brackets spanning multiple lines.

        It will set the following:

        - self.all_statement_tokens: a list of all the tokens in the statement
        - self.bad_token: the token identified as causing the problem based on offset.
        - self.begin_brackets: a list of open brackets '([{' not yet closed
        - self.end_bracket: an unmatched closing bracket ')]}' signaling an error
        """

        previous_row = -1
        previous_token = None
        self.prev_token = None
        continuation_line = False

        for token in source_tokens:
            # is this a new statement?
            if token.start_row > previous_row:
                if previous_token is not None:
                    continuation_line = previous_token.line.endswith("\\\n")
                if token.start_row <= self.linenumber and not self.begin_brackets:
                    self.all_statement_tokens = []
                previous_row = token.start_row

            # Did we collect all the tokens belonging to the statement?
            if (
                token.start_row > self.linenumber
                and not self.begin_brackets
                and not continuation_line
            ):
                break

            self.all_statement_tokens.append(token)
            # The offset seems to be different depending on Python versions,
            # sometimes matching the beginning of a token, sometimes the end.
            # Furthermore, the end of a token (end_col) might be equal to
            # the beginning of the next (start_col).
            if (
                token.start_row == self.linenumber
                and token.start_col <= offset <= token.end_col
                and self.bad_token is None
                and token.string.strip()
            ):
                self.bad_token = token
                if self.bad_token.is_comment():
                    self.bad_token = self.prev_token
            elif (
                token.string.strip()
                and not token.is_comment()
                and self.bad_token is None
            ):
                self.prev_token = token

            previous_token = token
            if token.is_not_in("()[]}{"):
                continue

            if token.is_in("([{"):
                self.begin_brackets.append(token)
            elif token.is_in(")]}"):  # Does it match or not
                self.end_bracket = token
                if not self.begin_brackets:
                    break
                else:
                    open_bracket = self.begin_brackets.pop()
                    if not matching_brackets(open_bracket, token):
                        self.begin_brackets.append(open_bracket)
                        break
                    else:
                        self.end_bracket = None

    def remove_meaningless_tokens(self):
        """Given a list of tokens, remove all space-like tokens and comments."""
        index = 0
        tokens = []
        for tok in self.all_statement_tokens:
            if not tok.string.strip() or tok.is_comment():
                continue
            tokens.append(tok)
            if tok is self.bad_token:
                self.bad_token_index = index
            index += 1
        return tokens
