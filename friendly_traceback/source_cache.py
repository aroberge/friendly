"""source_cache.py

Used to cache and retrieve source code.
This is especially useful when a custom REPL is used.
"""

import os.path

# TODO: use the undocumented linecache.getlines  (note the final s)
# from Python's standard library.


class Cache:
    """Class used to store source of files and similar objects"""

    def __init__(self):
        self.cache = {}
        self.context = 3
        self.ages = {}  # only for physical files

    def add(self, filename, source):
        """Adds a source (as a string) corresponding to a filename in the cache.

        The filename can be a true file name, or a fake one, like
        <console:42>, used for saving an REPL entry.

        If it is a true file, we record the last time it was modified.
        """
        self.cache[filename] = source
        if os.path.isfile(filename):
            self.ages[filename] = os.path.getmtime(filename)  # modification time

    def get_source_lines(self, filename):
        """Given a filename, returns the corresponding source, either
        from the cache or from actually opening the file.

        If the filename corresponds to a true file, and the last time
        it was modified differs from the recorded value, a fresh copy
        is retrieved.

        The contents is stored as a string and returned as a list of lines.
        If no source can be found, an empty list is returned.
        """
        # The main reason we care about ensuring we have the latest version
        # of a given file is situations where we could
        # 'edit and run' multiple times a given file. We need to ensure that
        # the content shown by the traceback is accurate.

        if os.path.isfile(filename):
            last_modified = os.path.getmtime(filename)  # modification time
            if filename not in self.cache:
                source, lines = self._get_file_source(filename)
                if source is not None:
                    self.add(filename, source)
            elif filename in self.ages and last_modified != self.ages[filename]:
                # modified; get fresh copy
                source, lines = self._get_file_source(filename)
                if source is not None:
                    self.add(filename, source)
                else:  # had problems retrieving fresh copy
                    source = self.cache[filename]
                    lines = source.split("\n")
            else:
                source = self.cache[filename]
                lines = source.split("\n")
        elif filename in self.cache:
            source = self.cache[filename]
            lines = source.split("\n")
        else:
            lines = []

        return lines

    def _get_file_source(self, filename):
        """Helper function to retrieve a file"""
        try:
            with open(filename, encoding="utf8") as f:
                lines = f.readlines()
                source = "".join(lines)
        except Exception:
            lines = []
            source = None
        return source, lines

    def get_formatted_partial_source(self, filename, linenumber, offset):
        """Formats a few lines around a 'bad line', and returns
        the formatted source as well as the content of the 'bad line'.
        """
        lines = self.get_source_lines(filename)
        if not lines:
            return "", ""

        begin = max(0, linenumber - self.context)
        partial_source, bad_line = highlight_source(
            linenumber,
            linenumber - begin - 1,
            # it is useful to show at least one more line when a statement
            # continues beyond the current line.
            lines[begin : linenumber + 1],
            offset=offset,
        )
        return partial_source, bad_line


cache = Cache()


def highlight_source(linenumber, index, lines, offset=None):
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
    if lines is None:  # This is the case for some SyntaxError cases
        return "", ""
    if index is None:
        print("problem in highlight_source(): index is None")
        index = 0

    # The weird index arithmetic below is based on the information returned
    # by Python's inspect.getinnerframes()

    new_lines = []
    problem_line = ""
    nb_digits = len(str(linenumber + index))
    no_mark = "       {:%d}: " % nb_digits
    with_mark = "    -->{:%d}: " % nb_digits
    if offset is not None:
        offset_mark = " " * (8 + nb_digits + offset) + "^"

    for i, line in enumerate(lines, linenumber - index):
        if i == linenumber:
            num = with_mark.format(i)
            problem_line = line
            new_lines.append(num + line.rstrip())
            if offset is not None:
                new_lines.append(offset_mark)
        else:
            num = no_mark.format(i)
            new_lines.append(num + line.rstrip())
    return "\n".join(new_lines), problem_line
