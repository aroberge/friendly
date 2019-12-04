"""utils.py

A few useful objects which do not naturally fit anywhere else.
"""
import token as token_module
import tokenize
import os.path

from io import StringIO


class Token:
    """Token as generated from tokenize.generate_tokens written here in
       a more convenient form for our purpose.
    """

    def __init__(self, token):
        self.type = token[0]
        self.string = token[1]
        self.start = self.start_line, self.start_col = token[2]
        self.end = self.end_line, self.end_col = token[3]
        # ignore last parameter which is the logical line

    def __repr__(self):
        return "{type:<10}{string:<25} {start:^10} {end:^10}".format(
            type=token_module.tok_name[self.type],
            string=self.string,
            start=str(self.start),
            end=str(self.end),
        )


def collect_tokens(line):
    """Makes a list of tokens on a line, ignoring spaces and comments"""
    tokens = []
    try:
        for tok in tokenize.generate_tokens(StringIO(line).readline):
            token = Token(tok)
            if not token.string.strip():  # ignore spaces
                continue
            if token.type == tokenize.COMMENT:
                break
            tokens.append(token)
    except tokenize.TokenError:
        return []
    except Exception as e:
        print("%s raised in utils.collect_tokens" % repr(e))

    return tokens


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


def _tokenize(source):
    """Prints tokens found in source, excluding spaces and comments.

       This is occasionally useful to use at the console during development.
    """
    lines = source.split("\n")
    print(
        "{type:<10}{string:<25} {start:^12} {end:^12}".format(
            type="Type", string="String", start="Start", end="End"
        )
    )
    print("-" * 60)
    for line in lines:
        tokens = collect_tokens(line)
        for token in tokens:
            print(token)
