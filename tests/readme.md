# Readme for tests

This directory contains files whose names begin by `trb_`: these are used
to generate the traceback for the documentation that lives in a separate
repository.

It also contains three subdirectories:

1. `except` contains test cases for exceptions that are raised while
   executing a program
2. `syntax` contains test cases for exceptions, such as `SyntaxError` that
   prevent a program from being compiled, let alone being executed by Python.
3. `unit` contains tests cases for specific parts of friendly-traceback.
