Usage
=====

There are three basic ways of using friendly-traceback.

1. As an exception hook::

    import friendly_traceback
    friendly_traceback.install()  # sys.excepthook = friendly_traceback.explain


2. Catching exceptions locally::

    try:
        # Some code
    except Exception:
        friendly_traceback.explain(*sys.exc_info())


3. When launching a Python script (or the REPL)::

    python -m friendly_traceback myscript.py


By default, friendly tracebacks are written to ``sys.stderr``.
However, it is possible to override this choice.

Let's look at each of these three cases in a bit more detail.

As an exception hook
---------------------

By default, installing Friendly-traceback as an exception hook has all the
output printed in stderr. This can be redirected to any writable stream
by using::

    friendly_traceback.install(redirect=stream)

A special option is available where the output is captured instead::

    friendly_traceback.install(redirect="capture")

Later, this captured output can be retrieved using::

    output = friendly_traceback.get_output(flush=True)

The value shown for the ``flush`` parameter is the default; this means that
the output will be cleared once it has been retrieved. If this is not the
desired behaviour, simply use ``flush=False``.

Catching exception locally
--------------------------

Another way to use Friendly-traceback is to catch exceptions where they
are expected to arise, such as::


    try:
        # Some code
    except Exception:
        friendly_traceback.explain(*sys.exc_info())

This uses the default of writing to ``sys.stderr``.
One can also redirect the output to any stream, as mentioned before.
The full set of arguments is::

    try:
        # Some code
    except Exception:
        friendly_traceback.explain(etype, value, tb, redirect=None)

where the default of ``None`` indicates that ``sys.stderr`` will be used.

From the command line
----------------------

.. code-block:: none

    $ python -m friendly_traceback -h
    usage: -m [-h] [--lang LANG] [--level LEVEL] [--as_main] [source]

    Friendly-traceback makes Python tracebacks easier to understand.

            Note: the values of the verbosity level described below are:
                0: Normal Python tracebacks
                1: Default - does not need to be specified
                9: Normal Python tracebacks appended at the end of the friendly
                display.

            Other values may be available, as we try to find the most useful
            settings for beginners.

    positional arguments:
      source

    optional arguments:
      -h, --help     show this help message and exit
      --lang LANG    This sets the language used by Friendly-tracebacks. Usually
                     this is a two-letter code such as 'fr' for French.
      --level LEVEL  This sets the "verbosity" level, that is the amount of
                     information provided.
      --as_main      Runs the program as though it was the main script. In case of
                     problems with the code, it can lead to some difficult to
                     understand tracebacks.
