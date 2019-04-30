"""formatter.py

"""


def format_traceback(info):
    """ Provides a basic explanation for a traceback.

        Rather than a standard explanation, we provide an example with
        four different parts, which are noted as such in the code.

        # 1. Generic explanation
        Python exception:
            NameError: name 'c' is not defined

        A NameError exception indicates that a variable or
        function name is not known to Python.
        Most often, this is because there is a spelling mistake.
        However, sometimes it is because the name is used
        before being defined or given a value.

        # 2. Likely cause
        Likely cause:
            In your program, the unknown name is 'c'.

        # 3. last call made
        Execution stopped on line 48 of file 'tb_common.py'.

           46:                     mod = __import__(name)
           47:                     if function is not None:
        -->48:                         getattr(mod, function)()
           49:                 except Exception:

        # 4. origin of the exception (could be the same as 3.)
        Exception raised  on line 8 of file 'raise_name_error.py'.

            6:     # Should raise NameError
            7:     a = 1
        --> 8:     b = c
            9:     d = 3

    """
    result = [""]
    for item in [
        "header",
        "generic",
        "cause",
        "last_call header",
        "last_call source",
        "last_call variables",
        "exception_raised header",
        "exception_raised source",
        "exception_raised variables",
    ]:
        if item in info:
            result.append(info[item])

    return "\n".join(result)
