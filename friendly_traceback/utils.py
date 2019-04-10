"""utils.py"""

CONTEXT = 4


def get_partial_source(filename, linenumber, offset):
    with open(filename) as f:
        lines = f.readlines()
    begin = linenumber - CONTEXT
    return highlight_source(
        linenumber, linenumber - 1, lines[begin:linenumber], offset=offset
    )


def highlight_source(linenumber, index, lines, offset=None):
    """Displays a few relevant lines from a file, showing line numbers
       and identifying a particular line.
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
        else:
            num = no_mark.format(i)
        new_lines.append(num + line.rstrip())
        i += 1
    if offset is not None:
        new_lines.append(offset_mark)
    return "\n".join(new_lines)
