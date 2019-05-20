"""source_cache.py

Used to cache and retrieve source code.
This is especially useful when a custom REPL is used.
"""


class Cache:
    def __init__(self):
        self.cache = {}
        self.context = 4

    def add(self, filename, source, string=False):
        self.cache[filename] = source
        if string:
            self.cache["<string>"] = filename
        elif "<string>" in self.cache:
            del self.cache["<string>"]

    def get_copy(self):
        """Gets a copy of the cache"""
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
            if key != "<string>":
                self.add(key, other_cache[key])
        else:
            if "<string>" in other_cache:
                filename = other_cache["<string>"]
                self.add(filename, other_cache[filename], string=True)

    def get_true_filename(self, filename):
        if filename != "<string>" or "<string>" not in self.cache:
            return filename
        return self.cache[filename]

    def get_source(self, filename):
        filename = self.get_true_filename(filename)
        if filename in self.cache:
            source = self.cache[filename]
            print("source in self.cache = ", source)
            lines = source.split("\n")
            print("lines = ", lines)
        else:
            try:
                with open(filename, encoding="utf8") as f:
                    lines = f.readlines()
                    self.cache[filename] = "".join(lines)
            except Exception:
                lines = []
        return lines

    def _get_partial_source(self, filename, linenumber, offset):
        lines = self.get_source(filename)
        if not lines:
            print("Problem: source of %s is not available" % filename)
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
    # The following are left-over diagnostic from the hack to integrate
    # into Idle; they are harmless tests which could potentially be useful.
    if lines is None:
        return "", ""
    if index is None:
        print("problem in highlight_source(): index is None")
        index = 0
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
