Adding an Exception for a Syntax Error
=======================================

.. important::

    Doing a task such as described here assumes that you are only adding to the existing code, mostly in the form of
    additions of test files and functions in two other files.
    Assuming this is the case, you can work directly from the
    masters branch, without needing to add a separate branch.
    Of course, you may create a separate branch if you prefer
    to do so; its name should be based on the issue number that
    you create.

This primarily describes the situation where you wish to add friendly
tracebacks for an Exception that is not already included.
Cases where an already included Exception is found to have
possible different causes, such as ``IndentationError``,
but which are not properly taken care of by the existing code
are covered near the end of this document.

.. note::

    **Checklist**

    The following are the required steps before a pull request.
    Each item is explained in a different section below. If you find
    the instructions unclear, please do not hesitate to reach out.

        - File an issue indicating that you are planning to work on a
          given exception.
        - Add test case
            - Add raise_some_exception.py file
            - Add catch_some_exception.py file
        - Add generic information
        - Add specific information
        - Execute catch_some_exception.py and confirm visually it works as expected
        - Run pytest and confirm that your new test is included
        - Make a pull request

    The following are optional steps; they will need to be done at some point
    but, apart for possible translations in languages other than French,
    I can definitely take care of this.

        - Add case to tests/tb_common.py
            - Run tests/tb_english.py and ensure docs/tracebacks_en.rst shows
              the expected result
        - Run make_tb.bat or do the equivalent on non Windows computer
        - Confirm that all docs/tracebacks_xx.rst include the new exception
        - Add translation

Adding a test case
------------------

After you have filed an issue indicating that you wished to
adding coverage for an exception that is not previously
covered, you need to start by adding a test case.
As an example throughout, I will use the existing one for
``NameError``.


Raising an exception
~~~~~~~~~~~~~~~~~~~~~

Your test file name should start with ``raise_``,
such as ``raise_name_error.py``.  Here is the content of that file::

    """Contains a function that should raise NameError"""

    def test():
        """Should raise NameError"""
        b = c
        d = 3

    if __name__ == "__main__":
        import friendly_traceback
        friendly_traceback.install()
        test()

As you can see, it contains a single test function which, when run,
would generate the expected exception.
Note that we do not use an artificial ``raise NameError`` statement,
but a genuine example. This is important as we want the recorded
traceback to reflect what users might encounter in their own programs.

After creating this file, you should run it from the root
directory of this repository, with something like::

    python tests/raise_name_error.py

Assuming that your OS default language is either English, or a
language for which translations do not exists, the output should look something like the following:

.. code-block:: none

    Python exception:
        MyException: Some informative message

    No information is known about this exception.


If this is the case, you are ready to go to the next step.

Catching an exception
~~~~~~~~~~~~~~~~~~~~~

Now that you can run a script that can raise an exception,
you need to create a script that will catch it, and can
also be used by pytest which we use as our test runner.
Here's the content of ``catch_name_error.py``, with some
numbered comments added, to which we refer below::

    import friendly_traceback  # 1
    import sys

    def test_name_error():  # 2
        try:                # 3
            from . import raise_name_error  # for pytest
        except ImportError:
            import raise_name_error

        try:
            raise_name_error.test()  # 4
        except Exception:
            friendly_traceback.explain(*sys.exc_info(), redirect="capture")      # 5
        result = friendly_traceback.get_output()  # 6
        assert "NameError: name 'c' is not defined" in result  # 7
        return result  # 8


    if __name__ == "__main__":      # 9
        result = test_name_error()
        print(result)


1. The necessary import.
2. Defining a test function; the name of this function **must**
   start with ``test_``.
3. Depending on whether the test is run with all the others by pytest
   or whether it is run as a single test, we need to import the
   file raising the exception differently.
4. While friendly_traceback can be installed "globally", as an
   exception hook, we use it instead in a localized try/except
   statement.
5. By default, friendly_traceback outputs its result to sys.stderr.
   However, this can be redirected to any other user provided
   function. In addition, there is a "capture" mode, as indicated,
   which simply stores the result.
6. To retrieve the previously stored result, we use the
   ``get_output()`` method. By default, this method also empties
   the cache used to capture the output. There is an optional
   argument to change this behaviour but it would be counter
   productive in this situation as we wish our tests to be done
   independently.
7. Pytest checks for assertion errors. So, we include parts of
   what we expect to see in the output. This is usually the
   beginning of the line just below ``Python exception:`` that
   was shown when running something like ``raise_myexception.py``
   previously. For reliability, we should include more than
   just the name of the Exception. Just leave any information
   about the line and file number out, to avoid making the tests
   brittle if we were to change either. For example, we might
   discover that a given exception has more than one case
   (``IndentationError``, for example, has three cases) and we
   might want to number each individual test file.
8. We must return the previously captured result for independent
   testing.
9. By adding this, we can run something like::

      python tests/catch_name_error.py

   and see the expected result.

At this point, running pytest from the root directory should
work, and you should see your test case included.


Adding generic information
--------------------------

The main goal of friendly_tracebacks is to help beginners and/or
programmers whose knowledge of English is limited,
to understand more easily what a given exception means.
So, your first goal is to imagine that you are helping a beginner
understand what SomeException means, writing in English with
as little Python-specific jargon as possible.  Try to do
so in a short paragraph. Do not strive for perfection.
It is expected that we will hear from actual users
(teachers and students) using friendly_tracebacks and that we
will be able to improve the descriptions based on their feedback,
and not based on our own pre-conception.

Generic information about given exceptions is found in file
``friendly_traceback/generic_info.py``.
Here are the relevant parts of that file for the NameError
exception::

    def name_error(*args):
        _ = current_lang.lang
        return _(
            "    A NameError exception indicates that a variable or\n"
            "    function name is not known to Python.\n"
            "    Most often, this is because there is a spelling mistake.\n"
            "    However, sometimes it is because the name is used\n"
            "    before being defined or given a value.\n"
        )


    generic = {
        "IndentationError": indentation_error,
        "NameError": name_error,
        "SyntaxError": syntax_error,
        "Unknown": unknown,
    }

We use gettext for providing translations. You do not need to be
familiar with gettext for this doing this work.
For those that are familiar with gettext, the most common way
to use it is to **install** it globally, so that the function ``_``
is added to Python's builtins and can be used everywhere.
For reasons that will be explained elsewhere, we cannot do this
in this project.

.. todo::

    Explain why we do not install gettext globally.

We first define a function whose name reflects the exception
we wish to explain. Thus, for ``NameError``,
we defined ``name_error()``.
This function will receive some positional arguments that may be useful for some exceptions.  For the first run through, you can
assume that you can ignore these arguments.

Ideally, this function should be inserted sorted alphabetically
in the file.

The first line of the function is::

    _ = current_lang.lang

This ensures that translations done by gettext are handled correctly.

Next, we return a string enclosed by ``_( )``; this is a call to
gettext to retrieve the correct translation.

For clarity, instead of using triple-quoted strings, we use Python's
automatic concatenation of adjacent strings to format the text.
Experience has shown us that this makes it much easier to
write the corresponding translations using Poedit.
Each string should represent a single line of text, and end with
a single ``\n``.
In addition, each line should be indented by four spaces.
The latter both makes it easier to read the explanation when using
an REPL, and allows for automatic embedding with correct formatting
in the documentation using Sphinx.

Finally, at the very bottom of that file, you need to add an
entry to the dict of the form::

    "MyException": my_exception,

This entry should be added so as to respect the alphabetical order
used.

Add specific information
------------------------

Let's look again at the output for NameError.
At the top of the feedback given by friendly_traceback, we
see the following:

.. code-block:: none

    Python exception:
        NameError: name 'c' is not defined

The second line is the information given by Python.
Your goal should be to rephrase this information in a way that
is possibly easier to understand by beginners **and** which can
be translated into languages other than English.
It should also follow naturally from your generic information.

In some cases, such as ``SyntaxError``, we might need the actual
source code in order to provide some very specific information.
For now, we assume that this is not the case.

Examining the line ``NameError: name 'c' is not defined``, we
see that it refers to a variable name, ``c``, which will almost
certainly be different when another user encounters a similar error.
Thus, our specific information should include this as a variable.

Specific information about given exceptions is found in file
``friendly_traceback/specific_info.py``.
Here are the relevant parts of that file for the NameError
exception::


    def name_error(etype, value):
        _ = current_lang.lang
        # value is expected to be something like
        #
        # NameError: name 'c' is not defined
        #
        # By splitting value using ', we can extract the variable name.
        return _("        In your program, the unknown name is '{var_name}'.\n").format(
            var_name=str(value).split("'")[1]
        )

    get_cause = {
        "IndentationError": indentation_error,
        "NameError": name_error,
        "SyntaxError": syntax_error,
    }

I assume that this is similar enough to the situation for the
generic information case that it does not warrant additional
explanation.  **The only difference is that each line of text should
be indented by 8 spaces.**

If you find that some additional explanation is needed,
please contact us or file an issue.


Test your work
--------------

Now that you have added the generic and specific information,
you should test again by running something like::

    python tests/raise_my_exception.py
    python tests/catch_my_exception.py

and confirm, in both cases that the result is acceptable.

Once this is done, run pytest from the root directory to make
sure that your new case is included in the test suite.

Make a pull request
--------------------

Before submitting your code, you should make sure that it
is formatted correctly according to `black <https://github.com/ambv/black>`_

However, we ask that you ensures that your added text
uses the one-line-per-string format described above.
If black reformats your code such that this is not the case, you
can temporarily turn it off and back on around the relevant
code.  Here's an example that we currently have in our code::

    # fmt: off
    return _(
        "\n"
        "    Python exception: \n"
        "        {name}: {value}\n"
        "\n"
        "{explanation}"
    ).format(name=name, value=value, explanation=explanation)
    # fmt: on

Next, you should make sure that your local repository is up to date
and fix any conflict that might be arising.

Finally, you can proceed with a `pull request <https://help.github.com/en/articles/creating-a-pull-request>`_.
If the information provided in that link is not clear, please do
not hesitate to ask for clarification.


Adding to an existing exception
-------------------------------

.. todo::

   To be written
