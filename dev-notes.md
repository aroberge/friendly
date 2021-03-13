# Developer notes

Friendly has no other dependencies than modules included in
Python's standard library. Python versions supported include 3.6, 3.7 and 3.8.

We use [black](https://github.com/python/black) for formatting and
[flake8](http://flake8.pycqa.org/en/latest/) for linting.
We also use [pytest](https://docs.pytest.org/en/latest/) for testing.

You can use `tox -p auto` to run black, flake8, and pytest in parallel.

Before submitting code, you should ensure that it conforms to the
formatting requirements and that all tests pass. Feel free to include
additional unit tests.

Currently, the code is only tested on Windows. The repository include
some batch (`.bat`) files which help to automate some processes, and are described
later in this document.


## Using virtual environments

In this section we document our use of virtual environments and naming
convention; the naming convention is only useful if you wish to make use
of the existing batch files.

1. Create a virtual environment for a given Python version:

        $ py -3.7 -m venv ./venv-friendly3.7

2. Activate the virtual environment; on Windows you can use

        $ ae 3.7

    Otherwise, you can presumably do something like:

        $ venv-friendly3.7/scripts/activate

3. Install the required dependencies for formatting, linting and testing

        $ python -m pip install -r requirements-dev.txt


4. If desired, deactivate the virtual environment and create new ones for
   other Python versions

        $ deactivate
        $ py -3.6 -m venv ./venv-friendly3.6

   etc.

## Editable version

To install friendly in editable mode (development version),
simply do

    $ python -m pip install -e .

from the root directory of the repository.

## Existing batch files

1. ae.bat

   Used to activate a virtual environment based on the Python version;
   Python 3.7 is the default.  Example usage:

        $ ae 3.6

2. make_trb.bat

   Used to create rst traceback files for the documentation. This assumes
   that a second repository exists and is found at the same directory level.
   No one but the repository owner should likely worry about this.
   It requires that Sphinx be installed in the default Python version.

3. pypi_upload.bat

   Script to upload to pypi; please ignore.

4. run_tests.bat

   Script to run the tests in all supported Python version, changing
   virtual environment as needed.


## Test coverage

Install pytest-cov and run the following:

     $ python -m pytest --cov=friendly --cov-report html

## Running a single test

It is often useful to run a single test case as you develop.
From the root directory, you can do something like the following:

    $ python -m friendly tests/syntax/raise_syntax_error17.py

And, if you want to quickly check a translation:

    $ python -m friendly --lang fr tests/syntax/raise_syntax_error17.py


## New translations

If you want to work on a translation, please see the online documentation.

Reminder note to self: the file friendly/make_pot.bat needs
to be run to update the catalog.
