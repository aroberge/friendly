"""utils.py"""

CONTEXT = 4
CONSOLE_SOURCE = {}
CONSOLE_NAME = "<Friendly console>"


def add_console_source(fake_filename, true_filename_and_source):
    CONSOLE_SOURCE[fake_filename] = true_filename_and_source


def get_source(filename):
    if filename in CONSOLE_SOURCE:
        _filename, source = CONSOLE_SOURCE[filename]
        lines = source.split("\n")
    else:
        with open(filename) as f:
            lines = f.readlines()
    return lines


def get_partial_source(filename, linenumber, offset):
    lines = get_source(filename)

    begin = max(0, linenumber - CONTEXT)
    # fmt: off
    return highlight_source(
        linenumber,
        linenumber-begin-1,
        lines[begin: linenumber+1],
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
    nb_digits = len(str(linenumber + index))
    no_mark = "       {:%d}: " % nb_digits
    with_mark = "    -->{:%d}: " % nb_digits
    if offset is not None:
        offset_mark = " " * (8 + nb_digits + offset) + "^"
    i = linenumber - index
    for line in lines:
        if i == linenumber:
            num = with_mark.format(i)
            if offset is not None:
                new_lines.append(num + line.rstrip())
                new_lines.append(offset_mark)
                break
        else:
            num = no_mark.format(i)
        new_lines.append(num + line.rstrip())
        i += 1
    return "\n".join(new_lines)
