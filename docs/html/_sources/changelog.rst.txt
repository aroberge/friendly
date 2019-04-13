Change Log
============

.. note::

    Unless otherwise noted, "with translation" means with French translation.


- Added ZeroDivisionError, with translation
- Added UnboundLocalError, with translation
- Took care of SystemExit and KeyboardInterrupt
- Reorgazed tests structure
- Added TabError, with translation
- Documentation: Dealing with Syntax Errors

Version 0.0.3
-------------

- Documentation: Adding new exception
- Added console (REPL) support
- Added test for unknown exception
- Added IndentationError, with translation
- Fixed install() option with capture

Version 0.0.2
-------------

- Added support for adding full Python traceback if level is set to higher number
- Added support for extracting preferred language from locale
- Added gettext support and French translation for NameError
- Added basic documentation with Sphinx - enabled on github.io
- Added basic test structure - using pytest
- Implemented and tested two ways of processing output: writing to stderr or capturing in buffer.
- Implemented "complete" processing of single exception (NameError)

Version 0.0.1
--------------

Initial commit and upload to Pypi.
