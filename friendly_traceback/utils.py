"""utils.py

A few useful objects which do not naturally fit anywhere else.
"""
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
    """Returns a list of words at a Damerau–Levenshtein distance of 1
    """
    # Since _leven() below returns maxDistance in cases that might require
    # even more changes, we compute changes up to distance 2 and only
    # retain those that are at a distance of 1
    similar_words = []
    for word in words:
        if word == "_":
            continue
        if _leven(word_with_typo, word, 2) == 1:
            similar_words.append(word)
    return similar_words


# The following code, including comments, has been copied from
# https://gist.github.com/giststhebearbear/4145811


def _leven(s1, s2, maxDistance):
    #  get smallest string so our rows are minimized
    s1, s2 = (s1, s2) if len(s1) <= len(s2) else (s2, s1)
    #  set lengths
    l1, l2 = len(s1), len(s2)

    #  We are simulatng an NM matrix where n is the longer string
    #  and m is the shorter string. By doing this we can minimize
    #  memory usage to O(M).
    #  Since we are simulating the matrix we only maintain two rows
    #  at a time the current row and the previous rows.
    #  A move from the current cell looking at the cell before it indicates
    #  consideration of an insert operation.
    #  A move from the current cell looking at the cell above it indicates
    #  consideration of a deletion
    #  Both operations are cost 1
    #  A move from the current cell to the cell up and to the left indicates
    #  an edit operation of 0 cost for a matching character and a 1 cost for
    #  a non matching characters
    #  no row has been previously computed yet, set empty row
    #  Since this is also a Damerau-Levenshtein calculation transposition
    #  costs will be taken into account. These look back 2 characters to
    #  determine optimal cost based on a possible transposition
    #  example: aei -> aie with levensthein has a cost of 2
    #  match a, change e->i change i->e => aie
    #  Damarau-Levenshtein has a cost of 1
    #  match a, transpose ei to ie => aie
    transpositionRow = None
    prevRow = None

    #  build first leven matrix row
    #  The first row represents transformation from an empty string
    #  to the shorter string making it static [0-n]
    #  since this row is static we can set it as
    #  curRow and start computation at the second row or index 1
    curRow = [x for x in range(0, l1 + 1)]

    # use second length to loop through all the rows being built
    # we start at row one
    for rowNum in range(1, l2 + 1):
        #  set transposition, previous, and current
        #  because the rowNum always increments by one
        #  we can use rowNum to set the value representing
        #  the first column which is indicitive of transforming TO
        #  the empty string from our longer string
        #  transposition row maintains an extra row so that it is possible
        #  for us to apply Damarau's formula
        transpositionRow, prevRow, curRow = prevRow, curRow, [rowNum] + [0] * l1

        #  consider if we have passed the max distance if all paths through
        #  the transposition row are larger than the max we can stop calculating
        #  distance and return the last element in that row and return the max
        if transpositionRow:
            if not any(cellValue < maxDistance for cellValue in transpositionRow):
                return maxDistance

        for colNum in range(1, l1 + 1):
            insertionCost = curRow[colNum - 1] + 1
            deletionCost = prevRow[colNum] + 1
            changeCost = prevRow[colNum - 1] + (
                0 if s1[colNum - 1] == s2[rowNum - 1] else 1
            )
            #  set the cell value - min distance to reach this
            #  position
            curRow[colNum] = min(insertionCost, deletionCost, changeCost)

            #  test for a possible transposition optimization
            #  check to see if we have at least 2 characters
            if 1 < rowNum <= colNum:
                #  test for possible transposition
                if (
                    s1[colNum - 1] == s2[colNum - 2]
                    and s2[colNum - 1] == s1[colNum - 2]
                ):
                    curRow[colNum] = min(
                        curRow[colNum], transpositionRow[colNum - 2] + 1
                    )

    #  the last cell of the matrix is ALWAYS the shortest distance between the two strings
    return curRow[-1]
