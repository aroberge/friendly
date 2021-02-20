"""Contains a class that compiles and stores all the information that
is relevant to the analysis of SyntaxErrors.
"""

from ..source_cache import cache
from .syntax_utils import matching_brackets
from .. import debug_helper
from .. import token_utils
from ..my_gettext import internal_error


# During the analysis for finding the cause of the error, we typically examine
# a "bad token" identified by Python as the cause of the error and often
# look at its two neighbours. If the bad token is the first one in a statement
# it does not have a token preceding it; if it is the last one, it does not
# have a token following it. By assigning a meaningless token value to these
# neighbours, the code for the analysis can be greatly simplified as we do
# not have to verify the existence of these neighbours.
MEANINGLESS_TOKEN = token_utils.tokenize(" ")[0]


class Statement:
    """Instances of this class contain all relevant information required
    for the various functions that attempt to determine the cause of
    SyntaxError.

    One main idea is to retrieve a "complete statement" where the
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

    def __init__(self, value, bad_line):
        # The basic information given by a SyntaxError
        self.filename = value.filename
        self.linenumber = value.lineno
        self.message = value.msg
        self.offset = value.offset

        # From the traceback, we were previously able ot obtain the line
        # of code identified by Python as being problematic.
        self.bad_line = bad_line  # previously obtained from the traceback
        self.statement = bad_line  # temporary assignment

        # The following will be obtained using offset and bad_line
        self.bad_token = None
        self.bad_token_index = 0
        self.prev_token = None  # meaningful token preceding bad token
        self.next_token = None  # meaningful token following bad token

        # SyntaxError produced inside f-strings occasionally require a special treatment
        self.fstring_error = self.filename == "<fstring>" or "f-string" in self.message

        self.all_statements = []  # useful to determine what lines to include in
        # the contextual display

        self.statement_tokens = []  # all tokens, including newlines, comments, etc.
        self.tokens = []  # meaningful tokens, used for error analysis; see docstring
        self.nb_tokens = 0  # number of meaningful tokens
        self.formatted_partial_source = ""
        self.source_lines = []  # lines of code for the source

        self.statement_brackets = []  # keep track of ([{ anywhere in a statement
        self.begin_brackets = []  # unclosed ([{  before bad token
        self.end_bracket = None  # single unmatched )]}

        self.first_token = None
        self.last_token = None

        # When using the friendly console (repl), SyntaxError might prevent
        # closing all brackets to complete a statement. Knowing this can be
        # useful during the error analysis.
        self.using_friendly_console = False
        if self.filename is not None:
            self.using_friendly_console = self.filename.startswith("<friendly")
        elif "too many statically nested blocks" not in self.message:
            # We know of only one case where filename should be None.
            debug_helper.log("filename is None in source_info.Statement")

        self.get_token_info()

    def get_token_info(self):
        """Obtain all the relevant information about the tokens in
        the file, with particular emphasis on the tokens belonging
        to the statement where the error is located.
        """
        if self.linenumber is not None:
            source_tokens = self.get_source_tokens()
            # self.all_statements and self.statement_tokens are set in the following
            self.obtain_statement(source_tokens)
            self.tokens = self.remove_meaningless_tokens()
            if not self.tokens:
                if len(self.all_statements) > 1:
                    self.statement_tokens = self.all_statements[-2]
                    self.tokens = self.remove_meaningless_tokens()
                else:
                    print(internal_error())
                    self.tokens = [token_utils.tokenize("Internal_error")[0]]

            self.statement = token_utils.untokenize(self.statement_tokens)
            if self.filename.startswith("<friendly-console"):
                if self.statement_brackets and not self.end_bracket:
                    # We got an error flagged before we had the chance to close
                    # brackets. Unclosed brackets are never a problem on their
                    # own in a console session - so, we make sure to close
                    # the brackets in order to be able to find the true cause
                    # of the error
                    add_token = ""
                    while self.statement_brackets:
                        bracket = self.statement_brackets.pop()
                        if bracket == "(":
                            add_token += ")"
                        elif bracket == "[":
                            add_token += "]"
                        else:
                            add_token += "}"

                    if self.tokens[0].string in [
                        "class",
                        "def",
                        "if",
                        "elif",
                        "while",
                        "for",
                        "except",
                        "with",
                    ]:
                        add_token += ":"

                    last_token = self.tokens[-1]
                    last_token = last_token.copy()
                    last_token.start_row += 1
                    last_token.string = last_token.line = add_token
                    self.tokens.append(last_token)

        elif "too many statically nested blocks" not in self.message:
            debug_helper.log("linenumber is None in source_info.Statement")

        if self.tokens:
            self.assign_individual_token_values()
        elif "too many statically nested blocks" not in self.message:
            debug_helper.log("No meaningful tokens in source_info.Statement")

    def get_source_tokens(self):
        """Returns a list containing all the tokens from the source."""
        source = ""
        if "f-string: invalid syntax" in self.message:
            source = self.bad_line
            try:
                exec(self.bad_line)
            except SyntaxError as e:
                self.offset = e.offset
                self.linenumber = 1
        if not source.strip():
            self.source_lines = cache.get_source_lines(self.filename)
            source = "".join(self.source_lines)
            if not source.strip():
                source = self.bad_line or "\n"
        return token_utils.tokenize(source)

    def assign_individual_token_values(self):
        """Assign values of previous and next to bad token and other
        related values.
        """
        self.nb_tokens = len(self.tokens)
        if self.nb_tokens >= 1:
            self.first_token = self.tokens[0]
            self.last_token = self.tokens[-1]

            if self.bad_token is None:
                self.bad_token = self.last_token
                self.bad_token_index = self.nb_tokens - 1
                if self.bad_token_index == 0:
                    self.prev_token = MEANINGLESS_TOKEN
                else:
                    self.prev_token = self.tokens[self.bad_token_index - 1]

            if self.bad_token_index == 0:
                self.prev_token = MEANINGLESS_TOKEN
            elif self.prev_token is None:
                self.prev_token = self.tokens[self.bad_token_index - 1]

        if self.last_token != self.bad_token:
            self.next_token = self.tokens[self.bad_token_index + 1]
        else:
            self.next_token = MEANINGLESS_TOKEN

    def format_statement(self):
        """Format the statement identified as causing the problem and possibly
        a couple of preceding statements, showing the line number and token identified.
        """
        # Some errors, like "Too many statistically nested blocs" prevent
        # Python from making a source available.
        if not self.statement_tokens:
            self.formatted_partial_source = ""
            return

        last = self.tokens[-1].end_row  # meaningful tokens

        for index, statement in enumerate(self.all_statements):
            last_token = statement[-1]
            if last - last_token.end_row < 5:
                break

        keep = self.all_statements[index:]  # noqa - warnings about index not defined
        start = keep[0][0].start_row

        tokens = []
        for statement in keep:
            tokens.extend(statement)

        partial_source = token_utils.untokenize(tokens)
        lines = partial_source.split("\n")
        nb_lines = len(lines)
        new_lines = []
        nb_digits = len(str(start + nb_lines))
        no_mark = "       {:%d}: " % nb_digits
        with_mark = "    -->{:%d}: " % nb_digits

        offset_mark = " " * (8 + nb_digits + self.offset) + "^"

        marked = False
        for i, line in enumerate(lines, start):
            if i == self.linenumber:
                num = with_mark.format(i)
                new_lines.append(num + line.rstrip())
                new_lines.append(offset_mark)
                marked = True
            elif marked:
                if not line.strip():  # do not add empty lines after problem line
                    break
                num = no_mark.format(i)
                new_lines.append(num + line.rstrip())
            elif i > self.linenumber + 5:
                # avoid printing to the end of the file if we have an unclosed bracket
                break
            else:
                num = no_mark.format(i)
                new_lines.append(num + line.rstrip())

        self.formatted_partial_source = "\n".join(new_lines)

    def obtain_statement(self, source_tokens):
        """This method scans the source searching for the statement that
        caused the problem. Most often, it will be a single line of code.
        However, it might occasionally be a multiline statement that
        includes code surrounded by some brackets spanning multiple lines.

        It will set the following:

        - self.statement_tokens: a list of all the tokens in the problem statement
        - self.bad_token: the token identified as causing the problem based on offset.
        - self.statement_brackets: a list of open brackets '([{' not yet closed
        - self.begin_brackets: a list of open brackets '([{' in a statement
          before the bad token.
        - self.end_bracket: an unmatched closing bracket ')]}' signaling an error
        - self.all_statements: list of all individual identified statements up to
          and including the problem statement.
        """

        previous_row = -1
        previous_row_non_space = -1
        previous_token = None
        continuation_line = False
        last_closing = None

        for token in source_tokens:
            # Did we collect all the tokens belonging to the bad statement?
            if (  # is the bad token identified as the very first token of a new line
                token.string.strip()
                and token.start_row == self.linenumber
                and token.start_col <= self.offset <= token.end_col
                and previous_token is not None
                and previous_token.string.strip()
                and previous_token.start_row < token.start_row
                and token.is_not_in(")]}")
            ):
                break
            if (
                token.start_row > self.linenumber
                and (last_closing is None or token.start_row > last_closing.start_row)
                and not continuation_line
            ):
                if not self.statement_brackets:
                    break
                # perhaps we have some unclosed bracket causing the error
                # and we meant to start a new statement
                elif token.is_in(
                    [
                        "async",
                        "await",
                        "class",
                        "def",
                        "return",
                        "elif",
                        "import",
                        "try",
                        "except",
                        "finally",
                        "with",
                        "while",
                        "yield",
                        # ";",
                    ]
                ):
                    break
                elif self.bad_token == ":":
                    break
                elif token.is_in(["if", "else", "for"]):
                    if token.start_row > previous_row_non_space:
                        # the keyword above likely starts a new statement
                        break
            if token.string.strip():
                previous_row_non_space = token.end_row

            # is this a new statement?
            # Valid statements will have matching brackets (), {}, [].
            # A new statement will typically start on a new line and will be
            # preceded by valid statements.

            # An initial version was based on the assumption that any semi-colon
            # would be used correctly and would indicate the end of a statement;
            # however, I am guessing that it more likely indicates
            # a typo, and that the user wanted to write a comma or a colon, so I
            # do not treat them in any special way.
            if token.start_row > previous_row:
                if previous_token is not None:
                    continuation_line = previous_token.line.endswith("\\\n")
                if token.start_row <= self.linenumber and not self.statement_brackets:
                    if self.statement_tokens:
                        self.all_statements.append(self.statement_tokens[:])
                    self.statement_tokens = []
                    self.begin_brackets = []
                    last_closing = None
                previous_row = token.start_row

            self.statement_tokens.append(token)
            # The offset seems to be different depending on Python versions,
            # sometimes matching the beginning of a token, sometimes the end.
            # Furthermore, the end of a token (end_col) might be equal to
            # the beginning of the next (start_col).
            if (
                token.start_row == self.linenumber
                and token.start_col <= self.offset <= token.end_col
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
                self.statement_brackets.append(token.string)
                if self.bad_token is None or self.bad_token is token:
                    self.begin_brackets.append(token)
            elif token.is_in(")]}"):
                self.end_bracket = token
                last_closing = token
                if not self.statement_brackets:
                    break
                else:
                    open_bracket = self.statement_brackets.pop()
                    if not matching_brackets(open_bracket, token.string):
                        self.statement_brackets.append(open_bracket)
                        break
                    else:
                        self.end_bracket = None

        if self.statement_tokens:  # Protecting against EOF while parsing
            last_line = token_utils.untokenize(self.statement_tokens)
            if not last_line.strip():
                if self.all_statements:
                    self.statement_tokens = self.all_statements[-1]
            else:
                self.all_statements.append(self.statement_tokens)

    def remove_meaningless_tokens(self):
        """Given a list of tokens, remove all space-like tokens and comments;
        also assign the index value of the bad token.
        """
        index = 0
        tokens = []
        for tok in self.statement_tokens:
            if not tok.string.strip() or tok.is_comment():
                continue
            tokens.append(tok)
            if tok is self.bad_token:
                self.bad_token_index = index
            index += 1
        return tokens
