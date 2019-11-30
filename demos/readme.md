# Demos readme

This directory contains a few demonstration files

## custom_exception.py

Shows how to define custom exceptions that are ready to be used by
Friendly-traceback. While this is not required, we showed how to
support translations.

There is no point in running this file as a script.

## custom_exception_demo.py

This is a demo that generates a few exceptions (most of which are imported
from custom_exception.py), process them with Friendly-traceback, and
shows the result.

This script can be run from a command line.

## gui_demo.py

This is a demo GUI that should be run from a command line.

When importing a script and running it, any normal Python traceback is shown
in the console (command line) and the "friendly traceback" counterpart is
shown in a text window.

It is suggested that you open "custom_exception_demo.py" and run it; you
will need to interact from the console (command line) as if you were executing
that script from Python.

Note that this GUI could likely be significantly improved; it is included
only as a proof of concept.
Experienced GUI programmers should feel most welcome to contribute their
expertise and make this a more user-friendly demonstration.

## custom_formatter.py

A custom formatter which creates an html file from a given exception.

## demo_gettext.py

Provides translation support for the demos

## hello.py

A simple file used in a few places in the documentation for
friendly-traceback itself.

## `_gui.py`

Various GUI elements that do not depend on either `demo_gettext.py` or
`friendly_traceback` and would only clutter the code of demos if they were
included in the script to be run.
