Adding an Exception
===================

This primarily describes the situation where you wish to add friendly
tracebacks for an Exception that is not already included.
**It does not apply to** ``SyntaxError`` **and its subclasses,**
``IndentationError`` and ``TabError``, **which need to be dealt separately.**

.. note::

    **Checklist**

    The following are the required steps before a pull request.
    Each item is explained in a different section below. If you find
    the instructions unclear, please do not hesitate to reach out.

        - File an issue indicating that you are planning to work on a
          given exception.
        - Add test case
        - Run pytest and confirm that your new test is included
        - Add generic information
        - Add specific information
        - Execute test_some_exception.py and confirm visually it works as expected
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
``UnboundLocalError``. I am documenting the process as I go through.

In this project, we use `pytest <https://docs.pytest.org/en/latest/>`_ and
simple assertion-based tests.


Your test file name should start with ``test_``,
such as ``test_unbound_local_error.py``.  Here is the content of that file,
with some numbered comments added::

    import friendly_traceback
    import sys


    def test_unbound_local_error():    # 1
        """Should raise UnboundLocalError"""
        a = 1

        def inner():
            a += 1

        try:
            inner()   # 2
        except Exception:
            friendly_traceback.explain(*sys.exc_info(), redirect="capture")  # 3
        result = friendly_traceback.get_output()  # 4
        assert "UnboundLocalError" in result  # 5
        return result  # 6


    if __name__ == "__main__":
        print(test_unbound_local_error())  # 7


1. Test functions should start with `test_`, so as to be recognized by pytest.
2. The code raising an error is inserted in a try/except clause.
   Friendly-traceback can be installed globally as an exception hook but
   this would not work when using pytest.
3. By default, friendly_traceback outputs its result to sys.stderr.
   However, this can be redirected to any other user provided
   function. In addition, there is a "capture" mode, as indicated,
   which simply stores the result.
4. To retrieve the previously stored result, we use the
   ``get_output()`` method. By default, this method also empties
   the cache used to capture the output. There is an optional
   argument to change this behaviour but it would be counter
   productive in this situation as we wish our tests to be done
   independently.
5. Pytest checks for assertion errors. So, we include parts of
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
6. We must return the previously captured result for independent
   testing.
7. This enables us to run this test by itself, without Pytest.

So, let's see what happens if we do run this test by itself.

.. code-block:: none

    $ python tests/test_unbound_local_error.py

        Python exception:
           UnboundLocalError: local variable 'a' referenced before assignment

        No information is known about this exception.


        Execution stopped on line 15 of file 'test_unbound_local_error.py'.

          13:
          14:     try:
        -->15:         inner()
          16:     except Exception:


        Exception raised on line 12 of file 'test_unbound_local_error.py'.

          10:
          11:     def inner():
        -->12:         a += 1
          13:

Note the line:

.. code-block:: none

    No information is known about this exception.

We will soon want to correct this. However, before we do so,
in order to make our test more accurate, we replace the line::

    assert "UnboundLocalError" in result

by::

    assert "UnboundLocalError: local variable 'a' referenced before assignment" in result


Running with pytest
-------------------

This assumes that pytest is installed on your computer.
From the root directory, simply run::

    pytest

You should see your test file listed, and no test failures reported by pytest.

Adding generic information
--------------------------

The main goal of friendly_tracebacks is to help beginners and/or
programmers whose knowledge of English is limited,
to understand what a given exception means.
So, your first goal is to imagine that you are helping a beginner
understand what SomeException means, writing in English with
as little Python-specific jargon as possible.  Try to do
so in a short paragraph. Do not strive for perfection.
It is expected that we will hear from actual users
(teachers and students) using friendly_tracebacks and that we
will be able to improve the descriptions based on their feedback,
and not based on our own pre-conceptions.

Generic information about given exceptions is found in file
``friendly_traceback/generic_info.py``.
Here are the relevant parts of that file for the UnboundLocalError
exception, followed by some explications::

    def unbound_local_error(*args):
        _ = current_lang.lang
        return _(
            "    In Python, variables that are used inside a function are known as \n"
            "    local variables. Before they are used, they must be assigned a value.\n"
            "    A variable that is used before it is assigned a value is assumed to\n"
            "    be defined outside that function; it is known as a 'global'\n"
            "    (or sometimes 'nonlocal') variable. You cannot assign a value to such\n"
            "    a global variable inside a function without first indicating to\n"
            "    Python that this is a global variable, otherwise you will see\n"
            "    an UnboundLocalError.\n"
        )

    generic = {
        "IndentationError": indentation_error,
        "NameError": name_error,
        "SyntaxError": syntax_error,
        "TabError": tab_error,
        "UnboundLocalError": unbound_local_error,
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
we wish to explain. Thus, for ``UnboundLocalError``,
we defined ``unbound_local_error()``.
This is not strictly required but it makes it easier to find the
information when looking at the code.
This function will receive some positional arguments that
may be useful for some exceptions.  For the first run through, you can
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
In addition, **each such string should start with four spaces.**
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

.. note::

    In some cases, it could happen that no specific information, as
    described below, is needed. In this case, you should still define
    a function for the specific information, so that we know it has
    not been overlooked, but have that function simply return None.

Let's look again at the output for UnboundLocalError.
At the top of the feedback given by friendly_traceback, we
see the following:

.. code-block:: none

    Python exception:
        UnboundLocalError: local variable 'a' referenced before assignment

The second line is the information given by Python.
Your goal should be to rephrase this information in a way that
is possibly easier to understand by beginners **and** which can
be translated into languages other than English.
It should also follow naturally from your generic information.

In some cases, such as ``SyntaxError``, we might need the actual
source code in order to provide some very specific information.
For now, we assume that this is not the case.

Examining the line ``UnboundLocalError: local variable 'a' referenced before assignment``, we
see that it refers to a variable name, ``a``, which will almost
certainly be different when another user encounters a similar error.
Thus, our specific information should include this as a variable.

Specific information about given exceptions is found in file
``friendly_traceback/specific_info.py``.
Here are the relevant parts of that file for the UnboundLocalError
exception::


    def unbound_local_error(etype, value):
        _ = current_lang.lang
        # value is expected to be something like
        #
        # UnboundLocalError: local variable 'a' referenced before assignment
        #
        # By splitting value using ', we can extract the variable name.
        return _("        The variable that appears to cause the problem is '{var_name}'.\n"
                 "        Try inserting the statement\n"
                 "            global {var_name}\n"
                 "        as the first line inside your function.").format(
            var_name=str(value).split("'")[1]
        )


    get_cause = {
        "IndentationError": indentation_error,
        "NameError": name_error,
        "SyntaxError": syntax_error,
        "TabError": tab_error,
        "UnboundLocalError": unbound_local_error,
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

    python tests/test_my_exception.py

and confirm that the result is acceptable.

Once this is done, run pytest once again from the root directory to make
sure that your new case is included correctly in the test suite.

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

Additional optional steps
-------------------------

To be written.

Adding to tb_common
~~~~~~~~~~~~~~~~~~~

To be written.
