"""utils.py"""
import tokenize
import os.path

from io import StringIO

CONTEXT = 4
CACHED_STRING_SOURCES = {}


class Token:
    """Token as generated from tokenize.generate_tokens written here in
       a more convenient form for our purpose.
    """

    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start_line, self.start_col = token[2]
        self.end_line, self.end_col = token[3]
        # ignore last parameter which is the logical line


def collect_tokens(line):
    """Makes a list of tokens on a line, ignoring spaces"""
    tokens = []
    try:
        for tok in tokenize.generate_tokens(StringIO(line).readline):
            token = Token(tok)
            if not token.string.strip():  # ignore spaces
                continue
            if token.type == tokenize.COMMENT:
                break
            tokens.append(token)
    except Exception as e:
        print("%s raised while tokenizing line" % repr(e))

    return tokens


def cache_string_source(fake_filename, true_filename_and_source):
    CACHED_STRING_SOURCES[fake_filename] = true_filename_and_source


def get_source(filename):
    if filename in CACHED_STRING_SOURCES:
        _filename, source = CACHED_STRING_SOURCES[filename]
        lines = source.split("\n")
    else:
        with open(filename, encoding="utf8") as f:
            lines = f.readlines()
    return lines


def get_partial_source(filename, linenumber, offset):
    lines = get_source(filename)

    begin = max(0, linenumber - CONTEXT)
    # fmt: off
    return highlight_source(
        linenumber,
        linenumber - begin - 1,
        lines[begin: linenumber + 1],
        offset=offset
    )
    # fmt: on


def highlight_source(linenumber, index, lines, offset=None):
    """Displays a few relevant lines from a file, showing line numbers
       and identifying a particular line.

       When dealing with a SyntaxError and subclasses, offset is an
       integer normally used by Python to indicate the position of
       the error, like:

           if True
                  ^
        which, in this case, points to a missing colon. We use the same
        representation in this case.
    """
    new_lines = []
    problem_line = ""
    nb_digits = len(str(linenumber + index))
    no_mark = "       {:%d}: " % nb_digits
    with_mark = "    -->{:%d}: " % nb_digits
    if offset is not None:
        offset_mark = " " * (8 + nb_digits + offset) + "^"
    i = linenumber - index
    for line in lines:
        if i == linenumber:
            num = with_mark.format(i)
            problem_line = line
            if offset is not None:
                new_lines.append(num + line.rstrip())
                new_lines.append(offset_mark)
                break
        else:
            num = no_mark.format(i)
        new_lines.append(num + line.rstrip())
        i += 1
    return "\n".join(new_lines), problem_line


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
