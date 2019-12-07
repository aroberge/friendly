"""analyze_syntax.py

Collection of functions useful attempting to determine the
cause of a SyntaxError and providing a somewhat detailed explanation.
"""

from keyword import kwlist
from io import StringIO
import re
import sys
import tokenize

from .my_gettext import current_lang
from . import utils
from .source_cache import cache

PYTHON_MESSAGES = []
LINE_ANALYZERS = []


def find_likely_cause(etype, value):
    """Given some source code as a list of lines, a linenumber
       (starting at 1) indicating where a SyntaxError was detected,
       a message (which follows SyntaxError:) and an offset,
       this attempts to find a probable cause for the Syntax Error.
    """
    filepath = value.filename
    linenumber = value.lineno
    offset = value.offset
    message = value.msg
    source_lines = cache.get_source(filepath)
    if not source_lines and filepath == "<stdin>":
        source_lines = [""]
        linenumber = 1
    return _find_likely_cause(source_lines, linenumber, message, offset)


def _find_likely_cause(source_lines, linenumber, message, offset):
    """Given some source code as a list of lines, a linenumber
       (starting at 1) indicating where a SyntaxError was detected,
       a message (which follows SyntaxError:) and an offset,
       this attempts to find a probable cause for the Syntax Error.
    """
    _ = current_lang.translate

    offending_line = source_lines[linenumber - 1]
    line = offending_line.rstrip()

    # If Python includes a descriptive enough message, we rely
    # on the information that it provides. We know that sometimes
    # this will yield to the wrong diagnostic but one of our objectives
    # is to explain in simpler language what Python means when it
    # raises a particular exception.

    for case in PYTHON_MESSAGES:
        cause = case(
            message=message,
            line=line,
            linenumber=linenumber,
            source_lines=source_lines,
            offset=offset,
        )
        if cause:
            return cause

    if message == "invalid syntax":
        notice = _(
            "I make an effort below to guess what caused the problem\n"
            "but I might guess incorrectly.\n\n"
        )
    else:
        notice = _(
            "Python gave us the following informative message\n"
            "about the possible cause of the error:\n\n"
            "    {message}\n\n"
            "However, I do not recognize this information and I have\n"
            "to guess what caused the problem, but I might be wrong.\n\n"
        ).format(message=message)

    # If not cause has been identified, we look at a single line
    # where the error has been found by Python, and try to find the source
    # of the error

    cause = analyze_last_line(line)
    if cause:
        return notice + cause

    # Failing that, we look for another type of common mistake. Note that
    # while we look for missing or mismatched brackets, such as (],
    # we also can sometimes identify other problems during this step.

    cause = look_for_missing_bracket(source_lines, linenumber, offset)
    if cause:
        return notice + cause

    # Eventually, we might add another step that looks at the entire code
    # For now, we just stop here

    return _(
        "Currently, I cannot guess the likely cause of this error.\n"
        "Try to examine closely the line indicated as well as the line\n"
        "immediately above to see if you can identify some misspelled\n"
        "word, or missing symbols, like (, ), [, ], :, etc.\n"
        "\n"
        "You might want to report this case to\n"
        "https://github.com/aroberge/friendly-traceback/issues\n"
        "\n"
    )


def add_python_message(func):
    """A simple decorator that adds a function the the list of functions
       that process a message given by Python.
    """
    PYTHON_MESSAGES.append(func)

    def wrapper(**kwargs):
        return func(**kwargs)

    return wrapper


@add_python_message
def assign_to_keyword(message="", line="", **kwargs):
    _ = current_lang.translate
    if not (
        message == "can't assign to keyword"  # Python 3.6, 3.7
        or message == "assignment to keyword"  # Python 3.6, 3.7
        or message == "cannot assign to keyword"  # Python 3.8
        or message == "cannot assign to None"  # Python 3.8
        or message == "cannot assign to True"  # Python 3.8
        or message == "cannot assign to False"  # Python 3.8
        or message == "cannot assign to __debug__"  # Python 3.8
    ):
        return

    tokens = utils.collect_tokens(line)
    while True:
        for token in tokens:
            word = token.string
            if word in kwlist or word == "__debug__":
                break
        else:
            raise RuntimeError("Fatal Error in analyze_syntax.assign_to_keyword")
        break

    if word in ["None", "True", "False", "__debug__"]:
        return _(
            "{keyword} is a constant in Python; you cannot assign it a value.\n" "\n"
        ).format(keyword=word)
    else:
        return _(
            "You were trying to assign a value to the Python keyword '{keyword}'.\n"
            "This is not allowed.\n"
            "\n"
        ).format(keyword=word)


@add_python_message
def assign_to_function_call(message="", line="", **kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to function call"  # Python 3.6, 3.7
        or message == "cannot assign to function call"  # Python 3.8
    ):
        if line.count("=") > 1:
            # we have something like  fn(a=1) = 2
            # or fn(a) = 1 = 2, etc.  Since there could be too many
            # combinations, we use some generic names
            fn_call = _("my_function(...)")
            value = _("some value")
            return _(
                "You wrote an expression like\n"
                "    {fn_call} = {value}\n"
                "where {fn_call}, on the left hand-side of the equal sign, is\n"
                "a function call and not the name of a variable.\n"
            ).format(fn_call=fn_call, value=value)

        info = line.split("=")
        fn_call = info[0].strip()
        value = info[1].strip()
        return _(
            "You wrote the expression\n"
            "    {fn_call} = {value}\n"
            "where {fn_call}, on the left hand-side of the equal sign, either is\n"
            "or includes a function call and is not simply the name of a variable.\n"
        ).format(fn_call=fn_call, value=value)


@add_python_message
def assign_to_literal(message="", line="", **kwargs):
    _ = current_lang.translate
    if (
        message == "can't assign to literal"  # Python 3.6, 3.7
        or message == "cannot assign to literal"  # Python 3.8
    ):
        info = line.split("=")
        literal = info[0].strip()
        name = info[1].strip()

        if name.isidentifier():
            # fmt: off
            suggest = _(
                " Perhaps you meant to write:\n"
                "    {name} = {literal}\n"
                "\n"
            ).format(literal=literal, name=name)
            # fmt: on
        else:
            suggest = "\n"

        return (
            _(
                "You wrote an expression like\n"
                "    {literal} = {name}\n"
                "where <{literal}>, on the left hand-side of the equal sign, is\n"
                "or includes an actual number or string (what Python calls a 'literal'),\n"
                "and not the name of a variable."
            ).format(literal=literal, name=name)
            + suggest
        )


@add_python_message
def break_outside_loop(message="", **kwargs):
    _ = current_lang.translate
    if "'break' outside loop" in message:
        return _(
            "The Python keyword 'break' can only be used "
            "inside a for loop or inside a while loop.\n"
        )


@add_python_message
def continue_outside_loop(message="", **kwargs):
    _ = current_lang.translate
    if "'continue' not properly in loop" in message:
        return _(
            "The Python keyword 'continue' can only be used "
            "inside a for loop or inside a while loop.\n"
        )


@add_python_message
def eol_while_scanning_string_literal(message="", **kwargs):
    _ = current_lang.translate
    if "EOL while scanning string literal" in message:
        return _(
            "You starting writing a string with a single or double quote\n"
            "but never ended the string with another quote on that line.\n"
        )


@add_python_message
def expression_cannot_contain_assignment(message="", **kwargs):
    _ = current_lang.translate
    if "expression cannot contain assignment, perhaps you meant" in message:
        return _(
            "One of the following two possibilities could be the cause:\n"
            "1. You meant to do a comparison with == and wrote = instead.\n"
            "2. You called a function with a named argument:\n\n"
            "       a_function(invalid=something)\n\n"
            "where 'invalid' is not a valid variable name in Python\n"
            "either because it starts with a number, or is a string,\n"
            "or contains a period, etc.\n"
            "\n"
        )


@add_python_message
def keyword_cannot_be_expression(message="", **kwargs):
    _ = current_lang.translate
    if "keyword can't be an expression" in message:
        return _(
            "You likely called a function with a named argument:\n\n"
            "   a_function(invalid=something)\n\n"
            "where 'invalid' is not a valid variable name in Python\n"
            "either because it starts with a number, or is a string,\n"
            "or contains a period, etc.\n"
            "\n"
        )


@add_python_message
def invalid_character_in_identifier(message="", **kwargs):
    _ = current_lang.translate
    if "invalid character in identifier" in message:
        return _(
            "You likely used some unicode character that is not allowed\n"
            "as part of a variable name in Python.\n"
            "This includes many emojis.\n"
            "\n"
        )


@add_python_message
def mismatched_parenthesis(
    message="", source_lines=None, linenumber=None, offset=None, **kwargs
):
    # Python 3.8; something like:
    # closing parenthesis ']' does not match opening parenthesis '(' on line
    _ = current_lang.translate
    pattern1 = re.compile(
        r"closing parenthesis '(.)' does not match opening parenthesis '(.)' on line (\d+)"
    )
    match = re.search(pattern1, message)
    if match is None:
        lineno = None
        pattern2 = re.compile(
            r"closing parenthesis '(.)' does not match opening parenthesis '(.)'"
        )
        match = re.search(pattern2, message)
        if match is None:
            return
    else:
        lineno = match.group(3)

    opening = match.group(2)
    closing = match.group(1)

    if lineno is not None:
        response = _(
            "Python tells us that the closing '{closing}' does not match "
            "the opening '{opening}' on line {lineno}.\n\n"
            "I will attempt to be give a bit more information.\n\n"
        ).format(closing=closing, opening=opening, lineno=lineno)
    else:
        response = _(
            "Python tells us that the closing '{closing}' does not match "
            "the opening '{opening}'.\n\n"
            "I will attempt to be give a bit more information.\n\n"
        ).format(closing=closing, opening=opening)

    response += look_for_missing_bracket(source_lines, linenumber, offset)

    return response


@add_python_message
def unterminated_f_string(message="", **kwargs):
    _ = current_lang.translate
    if "f-string: unterminated string" in message:
        return _(
            "Inside an f-string, which is a string prefixed by the letter f, \n"
            "you have another string, which starts with either a\n"
            "single quote (') or double quote (\"), without a matching closing one.\n"
        )


@add_python_message
def name_is_parameter_and_global(message="", line="", **kwargs):
    # something like: name 'x' is parameter and global
    _ = current_lang.translate
    if "is parameter and global" in message:
        name = message.split("'")[1]
        if name in line and "global" in line:
            newline = line
        else:
            newline = f"global {name}"
        return _(
            "You are including the statement\n\n"
            "    {newline}\n\n"
            "indicating that '{name}' is a variable defined outside a function.\n"
            "You are also using the same '{name}' as an argument for that\n"
            "function, thus indicating that it should be variable known only\n"
            "inside that function, which is the contrary of what 'global' implied.\n"
        ).format(newline=newline, name=name)


@add_python_message
def unexpected_character_after_continuation(message="", **kwargs):
    _ = current_lang.translate
    if "unexpected character after line continuation character" in message:
        return _(
            "You are using the continuation character '\\' outside of a string,\n"
            "and it is followed by some other character(s).\n"
            "I am guessing that you forgot to enclose some content in a string.\n"
            "\n"
        )


@add_python_message
def unexpected_eof_while_parsing(
    message="", source_lines=None, linenumber=None, offset=None, **kwargs
):
    # unexpected EOF while parsing
    _ = current_lang.translate
    if "unexpected EOF while parsing" not in message:
        return
    response = _(
        "Python tells us that the it reached the end of the file\n"
        "and expected more content.\n\n"
        "I will attempt to be give a bit more information.\n\n"
    )

    response += look_for_missing_bracket(source_lines, linenumber, offset)
    return response


@add_python_message
def unmatched_parenthesis(message="", linenumber=None, **kwargs):
    _ = current_lang.translate
    # Python 3.8
    if message == "unmatched ')'":
        bracket = name_bracket(")")
    elif message == "unmatched ']'":
        bracket = name_bracket("]")
    elif message == "unmatched '}'":
        bracket = name_bracket("}")
    else:
        return
    return _(
        "The closing {bracket} on line {linenumber} does not match anything.\n"
    ).format(bracket=bracket, linenumber=linenumber)


@add_python_message
def position_argument_follows_keyword_arg(message="", **kwargs):
    _ = current_lang.translate
    if "positional argument follows keyword argument" not in message:
        return
    return _(
        "In Python, you can call functions with only positional arguments\n\n"
        "    test(1, 2, 3)\n\n"
        "or only keyword arguments\n\n"
        "    test(a=1, b=2, c=3)\n\n"
        "or a combination of the two\n\n"
        "    test(1, 2, c=3)\n\n"
        "but with the keyword arguments appearing after all the positional ones.\n"
        "According to Python, you used positional arguments after keyword ones.\n"
    )


@add_python_message
def non_default_arg_follows_default_arg(message="", **kwargs):
    _ = current_lang.translate
    if "non-default argument follows default argument" not in message:
        return
    return _(
        "In Python, you can define functions with only positional arguments\n\n"
        "    def test(a, b, c): ...\n\n"
        "or only keyword arguments\n\n"
        "    def test(a=1, b=2, c=3): ...\n\n"
        "or a combination of the two\n\n"
        "    def test(a, b, c=3): ...\n\n"
        "but with the keyword arguments appearing after all the positional ones.\n"
        "According to Python, you used positional arguments after keyword ones.\n"
    )


@add_python_message
def python2_print(message="", **kwargs):
    _ = current_lang.translate
    if not message.startswith(
        "Missing parentheses in call to 'print'. Did you mean print("
    ):
        return
    message = message[59:-2]
    return _(
        "Perhaps you need to type print({message})?\n\n"
        "In older version of Python, 'print' was a keyword.\n"
        "Now, 'print' is a function; you need to use parentheses to call it.\n"
    ).format(message=message)


# ==================
# End of analysis of messages
# ==================


def analyze_last_line(line):
    """Analyzes the last line of code as identified by Python as that
       on which the error occurred."""
    tokens = utils.collect_tokens(line)  # tokens do not include spaces nor comments

    if not tokens:
        return

    for analyzer in LINE_ANALYZERS:
        cause = analyzer(tokens)
        if cause:
            return cause
    return


def add_line_analyzer(func):
    """A simple decorator that adds a function to the list
       of all functions that analyze a single line of code."""
    LINE_ANALYZERS.append(func)

    def wrapper(line):
        return func(line)

    return wrapper


# ==================
# IMPORTANT: causes are looked at in the same order as they appear below.
# Changing the order can yield incorrect results
# ==================


@add_line_analyzer
def detect_walrus(tokens):
    """Detecting if code uses named assignment operator := with an
       older version of Python.
    """
    _ = current_lang.translate
    if sys.version_info >= (3, 8):
        return False

    found_colon = False
    for token in tokens:
        if found_colon and token.string == "=":
            return _(
                "You appear to be using the operator :=, sometimes called\n"
                "the walrus operator. This operator requires the use of\n"
                "Python 3.8 or newer. You are using version {version}.\n"
            ).format(version=f"{sys.version_info.major}.{sys.version_info.minor}")

        found_colon = token.string == ":"


@add_line_analyzer
def assign_to_a_keyword(tokens):
    """Checks to see if line is of the form 'keyword = ...'

    Note: this is different from the above case where we got a useful
    message. Sometimes, all we get in such examples is "invalid syntax".
    """
    _ = current_lang.translate
    if len(tokens) < 2 or (tokens[0].string not in kwlist) or tokens[1].string != "=":
        return False

    return _(
        "You were trying to assign a value to the Python keyword '{keyword}'.\n"
        "This is not allowed.\n"
        "\n"
    ).format(keyword=tokens[0].string)


@add_line_analyzer
def confused_elif(tokens):
    _ = current_lang.translate
    name = None
    if tokens[0].string == "elseif":
        name = "elseif"
    elif tokens[0].string == "else" and len(tokens) > 1 and tokens[1].string == "if":
        name = "else if"
    if name:
        return _(
            "You meant to use Python's 'elif' keyword\n"
            "but wrote '{name}' instead\n"
            "\n"
        ).format(name=name)


@add_line_analyzer
def import_from(tokens):
    _ = current_lang.translate
    if len(tokens) < 4:
        return
    if tokens[0].string != "import":
        return
    third = tokens[2].string
    if third == "from":
        function = tokens[1].string
        module = tokens[3].string

        return _(
            "You wrote something like\n"
            "    import {function} from {module}\n"
            "instead of\n"
            "    from {module} import {function}\n"
            "\n"
        ).format(module=module, function=function)


@add_line_analyzer
def keyword_as_attribute(tokens):
    """Will identify something like  obj.True ..."""
    _ = current_lang.translate
    prev_word = None
    for token in tokens:
        word = token.string
        if prev_word == ".":
            if word in kwlist:
                return _(
                    "You cannot use the Python keyword {word} as an attribute.\n\n"
                ).format(word=word)
            elif word == "__debug__":
                return _("You cannot use the constant __debug__ as an attribute.\n\n")
        else:
            prev_word = word


@add_line_analyzer
def misplaced_quote(tokens):
    """This looks for a misplaced quote, something like
       info = 'don't' ...

    The clue we are looking for is a STRING token ('don')
    followed by a NAME token (t).
    """
    _ = current_lang.translate
    if len(tokens) < 2:
        return
    prev = tokens[0]
    for token in tokens:
        if prev.type == tokenize.STRING and token.type == tokenize.NAME:
            return _(
                "There appears to be a Python identifier (variable name)\n"
                "immediately following a string.\n"
                "I suspect that you were trying to use a quote inside a string\n"
                "that was enclosed in quotes of the same kind.\n"
            )
        prev = token


@add_line_analyzer
def missing_colon(tokens):
    """look for missing colon at the end of a line of code"""
    _ = current_lang.translate

    if tokens[-1].string == ":":
        return

    name = tokens[0].string

    if name == "class":
        name = _("a class")
        return _(
            "You wanted to define {class_}\n"
            "but forgot to add a colon ':' at the end\n"
            "\n"
        ).format(class_=name)
    elif name in ["for", "while"]:
        return _(
            "You wrote a '{for_while}' loop but\n"
            "forgot to add a colon ':' at the end\n"
            "\n"
        ).format(for_while=name)
    elif name in ["def", "elif", "else", "except", "finally", "if", "try"]:
        return _(
            "You wrote a statement beginning with\n"
            "'{name}' but forgot to add a colon ':' at the end\n"
            "\n"
        ).format(name=name)


@add_line_analyzer
def malformed_def(tokens):
    # need at least five tokens: def name ( ) :
    _ = current_lang.translate
    if tokens[0].string != "def":
        return False

    if (
        len(tokens) < 5
        or tokens[1].type != tokenize.NAME
        or tokens[2].string != "("
        or tokens[-2].string != ")"
        or tokens[-1].string != ":"
    ):
        name = _("a function or method")
        return _(
            "You tried to define {class_or_function} "
            "and did not use the correct syntax.\n"
            "The correct syntax is:\n"
            "    def name ( optional_arguments ):"
            "\n"
        ).format(class_or_function=name)
    fn_name = tokens[1].string
    if fn_name in kwlist:
        return _(
            "You tried to use the Python keyword '{kwd}' as a function name.\n"
        ).format(kwd=fn_name)

    # Lets look at the possibility that a keyword might have been used
    # as an argument or keyword argument. The following test is admiteddly
    # crude and imperfect, but it is the last one we do.

    prev_token_str = None
    parens = 0
    brackets = 0
    curly = 0
    for index, tok in enumerate(tokens):
        # Note, we know that a SyntaxError: invalid syntax occurred.
        # So, while some cases of the following might be ok, we assume here that
        # they might have caused the error. They might include things like:
        # def test(None ...)  or
        # def test(*None ...) or
        # def test(**None ...) or
        # def test(a, None ...)
        #       but not
        # def test(a=None ...) nor
        # def test(a=(None,...)) nor
        # def test(a = [1, None])
        char = tok.string
        if char == "(":
            parens += 1
        elif char == ")":
            parens -= 1
        if char == "[":
            brackets += 1
        elif char == "]":
            brackets -= 1
        if char == "{":
            curly += 1
        elif char == "}":
            curly -= 1

        elif char in kwlist and (
            (prev_token_str == "(" and index == 3)  # first argument
            or (
                parens % 2 == 1
                and brackets % 2 == 0
                and curly % 2 == 0
                and prev_token_str in [",", "*", "**"]
            )
        ):
            return _(
                "I am guessing that you tried to use the Python keyword\n"
                "{kwd} as an argument in the definition of a function.\n"
            ).format(kwd=char)
        prev_token_str = char


def look_for_missing_bracket(source_lines, max_linenumber, offset):
    """This function was initially looking for missing or mismatched brackets
        but it has expanded to include other cases.  By brackets here, we mean
        any one of: ()[]{}.

        We have a few cases to consider:

        1. mismatched brackets
        2. missing closing bracket
        3. missing comma between items.
        4. using = instead of : in a dict

        The last two cases will often result in an error being flagged at
        a given location such that the code up to that point would have
        an unclosed bracket.  For example, case 4 could be:

            ages = {'Alice' = 22, ...
                            ^

        and we would have an unclosed {.
    """
    _ = current_lang.translate
    source = "\n".join(source_lines)
    brackets = []
    beyond_brackets = []
    end_bracket = None
    tokens = tokenize.generate_tokens(StringIO(source).readline)
    token = None
    last_token = None
    try:
        for tok in tokens:
            if token is not None:
                last_token = token.string
            token = utils.Token(tok)
            if not token.string:
                continue
            if (
                token.start_line == max_linenumber
                and token.start_col >= offset
                or token.start_line > max_linenumber
            ):
                # We are beyond the location flagged by Python;
                if last_token == "=" and brackets:
                    _open_bracket, _start_line, _start_col = brackets.pop()
                    if _open_bracket == "{":
                        return _(
                            "It is possible that "
                            "you used an equal sign '=' instead of a colon ':'\n"
                            "to assign values to keys in a dict\n"
                            "before or at the position indicated by --> and ^.\n"
                        )
                    else:
                        brackets.append((_open_bracket, _start_line, _start_col))
                # Perhaps we are simply missing a comma between items.
                # If so, we should be able to find a closing bracket.
                if token.string in "([{":
                    beyond_brackets.append(token.string)
                elif token.string in ")]}":
                    if len(beyond_brackets) % 2 == 0:
                        end_bracket = token.string
                        break
                    else:
                        end_bracket = None
                        open_bracket = beyond_brackets.pop()
                        if not matching_brackets(open_bracket, token.string):
                            break
                continue

            # We are not beyond the location flagged by Python
            if token.string not in "()[]}{":
                continue
            if token.string in "([{":
                brackets.append((token.string, token.start_line, token.start_col))
            elif token.string in ")]}":
                # In some of the cases below, we include the offending lines at the
                # bottom of the error message as they might not be shown in the
                # partial source included in the traceback.
                if not brackets:
                    bracket = name_bracket(token.string)
                    _lineno = token.start_line
                    _source = f"\n    {_lineno}: {source_lines[_lineno-1]}\n"
                    shift = len(str(_lineno)) + token.start_col + 6
                    _source += " " * shift + "^\n"
                    return (
                        _(
                            "The closing {bracket} on line {linenumber}"
                            " does not match anything.\n"
                        ).format(bracket=bracket, linenumber=token.start_line)
                        + _source
                    )
                else:
                    open_bracket, open_lineno, open_col = brackets.pop()
                    if not matching_brackets(open_bracket, token.string):
                        bracket = name_bracket(token.string)
                        open_bracket = name_bracket(open_bracket)
                        _source = (
                            f"\n    {open_lineno}: {source_lines[open_lineno-1]}\n"
                        )
                        shift = len(str(open_lineno)) + open_col + 6
                        if open_lineno == token.start_line:
                            _source += " " * shift + "^"
                            shift = token.start_col - open_col - 1
                            _source += " " * shift + "^\n"
                        else:
                            _source += " " * shift + "^\n"
                            _lineno = token.start_line
                            _source += f"    {_lineno}: {source_lines[_lineno-1]}\n"
                            shift = len(str(_lineno)) + token.start_col + 6
                            _source += " " * shift + "^\n"
                        return (
                            _(
                                "The closing {bracket} on line {close_lineno} does not match "
                                "the opening {open_bracket} on line {open_lineno}.\n"
                            ).format(
                                bracket=bracket,
                                close_lineno=token.start_line,
                                open_bracket=open_bracket,
                                open_lineno=open_lineno,
                            )
                            + _source
                        )
    except tokenize.TokenError:
        pass

    if brackets:
        bracket, linenumber, start_col = brackets.pop()
        if end_bracket is not None:
            if matching_brackets(bracket, end_bracket):
                if bracket == "(":
                    return _(
                        "It is possible that you "
                        "forgot a comma between items in a tuple, \n"
                        "or between function arguments, \n"
                        "before the position indicated by --> and ^.\n"
                    )
                elif bracket == "[":
                    return _(
                        "It is possible that you "
                        "forgot a comma between items in a list\n"
                        "before the position indicated by --> and ^.\n"
                    )
                else:
                    return _(
                        "It is possible that you "
                        "forgot a comma between items in a set or dict\n"
                        "before the position indicated by --> and ^.\n"
                    )

        bracket = name_bracket(bracket)
        _source = f"\n    {linenumber}: {source_lines[linenumber-1]}\n"
        shift = len(str(linenumber)) + start_col + 6
        _source += " " * shift + "^\n"
        return (
            _("The opening {bracket} on line {linenumber} is not closed.\n").format(
                bracket=bracket, linenumber=linenumber
            )
            + _source
        )
    else:
        return False


def matching_brackets(bra, ket):
    return (
        (bra == "(" and ket == ")")
        or (bra == "[" and ket == "]")
        or (bra == "{" and ket == "}")
    )


def name_bracket(bracket):
    _ = current_lang.translate
    if bracket == "(":
        return _("parenthesis '('")
    elif bracket == ")":
        return _("parenthesis ')'")
    elif bracket == "[":
        return _("square bracket '['")
    elif bracket == "]":
        return _("square bracket ']'")
    elif bracket == "{":
        return _("curly bracket '{'")
    elif bracket == "}":
        return _("curly bracket '}'")
    else:  # Should never happen - help for diagnostic
        return f"Problem in analyze_syntax.py: '{bracket}'"
