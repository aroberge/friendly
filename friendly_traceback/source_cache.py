"""source_cache.py

Used to cache and retrieve source code.
This is especially useful when a custom REPL is used.

Note that we monkeypatch Python's linecache.getlines.
"""

import linecache
import time


old_getlines = linecache.getlines

idle_get_lines = None


class Cache:
    """Class used to store source of files and similar objects"""

    def __init__(self):
        self.cache = {}
        self.context = 4

    def add(self, filename, source):
        """Adds a source (received as a string) corresponding to a filename
        in the cache.

        The filename can be a true file name, or a fake one, like
        <friendly-console:42>, used for saving an REPL entry.
        These fake filenames might not be retrieved by Python's linecache
        which is why we keep a duplicate of anything we add to linecache.cache
        """
        # filename could be a Path object,
        # which does not have a startswith() method used below
        filename = str(filename)
        lines = [line + "\n" for line in source.splitlines()]
        entry = (len(source), time.time(), lines, filename)
        if not filename.startswith("<"):
            # Linecache never allows retrieving of such values,
            # so it is pointless to attempt to store them there.
            linecache.cache[filename] = entry
        self.cache[filename] = lines

    def remove(self, filename):
        """Removes an entry from the cache if it can be found."""
        if filename in self.cache:
            del self.cache[filename]
        if filename in linecache.cache:
            del linecache.cache[filename]

    def get_source_lines(self, filename, module_globals=None):
        """Given a filename, returns the corresponding source, either
        from the cache or from actually opening the file.

        If the filename corresponds to a true file, and the last time
        it was modified differs from the recorded value, a fresh copy
        is retrieved.

        The contents is stored as a string and returned as a list of lines,
        each line ending with a newline character.
        """
        if idle_get_lines is not None:
            lines = idle_get_lines(filename, None)  # noqa
        else:
            lines = old_getlines(filename, module_globals=module_globals)
            if not lines and filename in self.cache:
                lines = self.cache[filename]
        lines.append("\n")  # required when dealing with EOF errors
        return lines

    def get_formatted_partial_source(
        self, filename, linenumber, offset=None, text_range=None
    ):
        """Formats a few lines around a 'bad line', and returns
        the formatted source as well as the content of the 'bad line'.
        """
        lines = self.get_source_lines(filename)
        if not lines or not "".join(lines).strip():
            return "", ""

        begin = max(0, linenumber - self.context)
        partial_source, bad_line = highlight_source(
            linenumber,
            linenumber - begin - 1,
            # it is useful to show at least one more line when a statement
            # continues beyond the current line.
            lines[begin : linenumber + 1],
            offset=offset,
            text_range=text_range,
        )
        return partial_source, bad_line


cache = Cache()

# Monkeypatch linecache to make our own cached content available to Python.
linecache.getlines = cache.get_source_lines


def highlight_source(linenumber, index, lines, offset=None, text_range=None):
    """Extracts a few relevant lines from a file content given as a list
    of lines, adding line number information and identifying
    a particular line.

    When dealing with a ``SyntaxError`` or its subclasses, offset is an
    integer normally used by Python to indicate the position of
    the error with a ``^``, like::

        if True
              ^

    which, in this case, points to a missing colon. We use the same
    representation in this case.
    """

    # The weird index arithmetic below is based on the information returned
    # by Python's inspect.getinnerframes()
    new_lines = []
    problem_line = ""
    nb_digits = len(str(linenumber + index))
    no_mark = "       {:%d}: " % nb_digits
    with_mark = "    -->{:%d}: " % nb_digits

    offset_mark = None
    if offset is not None:
        offset_mark = " " * (8 + nb_digits + offset) + "^"

    text_range_mark = None
    if text_range is not None:
        begin, end = text_range
        text_range_mark = " " * (8 + nb_digits + begin + 1) + "^" * (end - begin)

    marked = False
    for i, line in enumerate(lines, linenumber - index):
        if i == linenumber:
            num = with_mark.format(i)
            problem_line = line
            new_lines.append(num + line.rstrip())
            if offset_mark is not None:
                new_lines.append(offset_mark)
            elif text_range_mark is not None:
                new_lines.append(text_range_mark)
            marked = True
        elif marked:
            if not line.strip():  # do not add empty line if last line
                break
            num = no_mark.format(i)
            new_lines.append(num + line.rstrip())
        else:
            num = no_mark.format(i)
            new_lines.append(num + line.rstrip())
    return "\n".join(new_lines), problem_line
