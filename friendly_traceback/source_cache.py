"""source_cache.py

Used to cache and retrieve source code.
This is especially useful when a custom REPL is used.
"""

# Some comments below refer to avant-idle. avant-idle is currently a
# project (currently unpublished) where we integrated Friendly-traceback
# and AvantPy into a modified version of Python's IDLE. This was done
# both to use as a demonstration and also to determine what functionality
# should be part of a public API.

import os.path


class Cache:
    """Class used to store source of files and similar objects"""

    def __init__(self):
        self.cache = {}
        self.context = 4
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

    def get_copy(self):
        """Gets a copy of the entire cache"""
        # This is used in avant-idle to pass the content of a cache in
        # the main process to a second process where an exception has been
        # raised.
        return self.cache

    def replace(self, other_cache):
        """Replaces the current cache by another"""
        # This is used in avant-idle to replace the content of the cache
        # in a process (where no storage normally takes place) by
        # that of another where the actual caching of the source is done.
        self.cache.clear()
        for key in other_cache:
            self.add(key, other_cache[key])

    def get_source(self, filename):
        """Given a filename, returns the corresponding source, either
           from the cache or from actually opening the file.

           If the filename corresponds to a true file, and the last time
           it was modified differs from the recorded value, a fresh copy
           is retrieved.

           The contents is stored a a string and returned as a list of lines.
           If no source can be found, an empty list is returned.
        """
        # The main reason we care about ensuring we have the latest version
        # of a given file is for the 'avant-idle' project where we could
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
        lines = self.get_source(filename)
        if not lines:
            return "", ""

        begin = max(0, linenumber - self.context)
        partial_source, bad_line = highlight_source(
            linenumber,
            linenumber - begin - 1,
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
    # The following if statements are left-over diagnostic
    # from the hack to integrate into Idle.
    # they are harmless tests which could potentially be useful.
    if lines is None:
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
