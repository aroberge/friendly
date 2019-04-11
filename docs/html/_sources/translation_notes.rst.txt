Notes on translations - using gettext
=====================================

.. important::

    There are many sites that explain how to use gettext. However, I found
    that, no matter what individual explanation I read, it was either
    incomplete, too specific, or otherwise glossing over some minor point
    that was important for my project.

    I wrote these notes mostly for myself, but they may be useful for
    you as well, perhaps even more so if you read a "standard" tutorial
    on using gettext first.


What is gettext?
----------------

gettext is basically a standardized way of internationalization (i18n)
and localization (l10n) of computer programs.

What this means for this project, is the translation of strings shown
to the user in their preferred language.


Structure of this project
-------------------------

Below, I make references to various files. Here's a simplified view of the
directory structure of this project, showing only a few relevant files::

    friendly-traceback/
        docs/
        friendly_traceback/
            locales/
                fr/
                    LC_MESSAGES/
                        fr.mo
                        fr.po
                messages.pot
            core.py
            make_pot.bat
        tests/
        setup.py

If you look at the repository on Github (or cloned locally), you will not
see the file ``make_pot.bat``.
I'll explain its role below.


How to use gettext
--------------------

Suppose we want to greet a user in their own language. For example,
in English we might have the following::

    print("Hello {name}".format(name=username))

while in French, we might have::

    print("Bonjour {name}".format(name=username))

The first thing to do would normally be to choose one of these forms as
our standard to be used as the reference for translation.
This is what I eventually chose to do for this project.
However, in the past, I have often
used a variation where words are written in the source file in uppercase
letter to make it more obvious to see if a translation is missing.

To indicate that a string needs to be translated, the common way is to
surround it by a function call, using ``_`` as the function name::

    print(  _( "Hello {name}" )  .format(name=username)  )

    # extra spaces above added for clarity

Next, we need to create a "template" file for translations.
I use ``pygettext.py`` included as a **tool** with Python.
It is very likely not on the normal path where it can be found by Python.
If you don't know where your python files are located, you can use
Python's REPL and do the following::

    >>> import sys
    >>> print(sys.prefix)
    C:\Users\andre\AppData\Local\Programs\Python\Python37

You can then navigate to the directory containing the Python version
you are using and will almost certainly
find ``pygettext.py`` under the ``tools\i18n`` subdirectory.

``pygettext`` will extract all the strings surronded by ``_( )`` in the
input file you specify and create a "template" file (identified by a ``.pot``
extension). To make my life easier, I simply type ``make_pot`` at the prompt
which executes the content of ``make_pot.bat`` (I'm using Windows)::

    python c:\users\andre\appdata\local\programs\python\python37\tools\i18n\pygettext.py -p locales *.py


- ``make_pot.bat`` is located in the same directory where the Python source files
  containing strings to be translated is located.
- I use ``python filename.py`` instead of simply ``filename.py`` as I set my
  computer default to open ``.py`` files with my preferred editor instead of
  executing them.
- The ``-p locales`` option specifies that the template file is going to be
  created (or updated) in the ``locales/`` directory
  (see above for the directory structure).
- Since I did not specify a name to be used for the template file, the default
  ``messages.pot`` will be used (again, see above).
- The source files scanned by pygettext (``*.py``) will be all the
  Python files in that directory.

There's more to be done; let's break this up into a few additional
sections.

Using Poedit
-------------

In principle, template files can be edited with any standard text editor
to create "portable object" (``.po``) files from a template file.
However, this is more easily done using
`Poedit <https://poedit.net/>`_ which is a free program especially designed
for this task. There is a paid "pro" version but it is really not required for
most tasks.  However, after a while, I have purchased it and found its
suggested translations usually very useful, at least as a starting point.

With Poedit, you have the choice of **creating** a new translation
either from a ``.pot`` file, or from a ``.po`` file. Open the relevant file,
choose a language, and start translating the various strings.

If you are **updating** an existing translation, open the ``.po`` file
and use Poedit's "Catalog" menu (fourth at the top of the menu
bar) to first update from the source (``messages.pot``) from which the
``.po`` file is derived.

Poedit gives the choice to translate for specific regions (e.g. fr_CA for
French used in Canada). For this project, I prefer to choose a generic
two-letter code (fr) as it is assumed to be the case in various places.

.. warning::

    If, for a given language, you **absolutely** need different language
    translations, specific to a region, please file an issue
    first so that this can be discussed and the impact on the rest of
    the code can be properly evaluated.

    One of the goals of this project is to provide easier to understand
    tracebacks than those provided by Python. These do not need to be
    absolutely perfect.

When it comes time to save the ``.po`` file, use a similar structure
as that shown above and save
it in the ``LC_MESSAGES`` directory of the appropriate language.
Note that Poedit will automatically save another file with
a ``.mo`` extension; this is a "machine object" (binary) file that will actually
be used by your program.

In addition to strings to be translated, ``.po`` files contain some
information about who translated the file and some copyright information.
In general, you might want to fill in the appropriate information.
Note that Poedit allows you to set your personal information (name
and email address) which will be automatically used, so that you don't
have to edit the created file by hand.

.. warning::

    Please, do not contribute translations to Friendly-traceback
    where you attribute the copyright to yourself.
    Either do not include any copyright information
    or attribute it to the Friendly-traceback project.

Telling Python to use the translations
--------------------------------------

In this project, the language selection is done in the file ``core.py``.
(See directory structure above.)
At the top of ``core.py``, ``gettext`` is imported.  Changing language
is done using the ``install_gettext`` method; the relevant parts are as follows::


    def install_gettext(self, lang):
        """Sets the current language for gettext."""
        try:
            gettext_lang = gettext.translation(
                lang,  # 1
                localedir=os.path.normpath(
                    os.path.join(os.path.dirname(__file__), "locales")  # 2
                ),
                languages=[lang],
                fallback=False,  # 3
            )
        except FileNotFoundError:
            lang = lang[:2]  # 4
            gettext_lang = gettext.translation(
                lang,
                localedir=os.path.normpath(
                    os.path.join(os.path.dirname(__file__), "locales")
                ),
                languages=[lang],
                fallback=True,  # 5
            )
        gettext_lang.install()  # 6


Here is an explanation for the numbered comments above:

    1. Indicates that translations will be found in files named ``lang + ".mo"``

    2. "Foolproof" way of locating the translation directory

    3. By default, fallback is ``False``; for clarity, we explicitly set it.
       If a request is made to use a non-existing translation, an exception is raised.

    4. If an exception is raised, we try again under the assumption that the
       value for ``lang`` was specific to a region (for example ``fr_CA``)
       and that we might have a translation for the generic version
       of that language.

    5. By using ``fallback=True``, the untranslated string (as it exists in
       the source file) is used instead.

    6. This adds the function named ``_`` to the builtins. So, it will be known
       to all other modules.  ``gettext_lang.install`` takes an
       optional argument which makes it possible to use different behaviour.
       By using the default, we do not provide any support for dealing with
       alternative translations based on quantity (singular/plural).


.. warning::

    When using flake8 (or likely other similar linters), ``_`` will be flagged
    as an unknown function.  This is taken care of in this project by adding::

        builtins =
            _

    to the ``.flake8`` configuration file.


.. warning::

    Every language has its own way to deal (or not) with plural forms of words.
    As mentioned, in principle, ``gettext`` offers a way to handle with the language specific complexities.
    In practice for this project, we assume a single form to be used.


Why are .mo files in the repository
-----------------------------------

When configuring the project, the automatically generated ``.gitignore`` file
include exclusion for ``.pot`` and ``.mo`` files.
The rationale is that these files are automatically generated (by some standard
programs) and it is generally suggested that such files not be included.

However, in this case, we want these files to be available to end users.
If someone clones the project, and needs to upload a version somewhere (e.g. pypi.org),
these generated files (at least the ``.mo`` files) need to be included.


Additional considerations
-------------------------

The description above accurately reflected what was in the code at the time
it was written.  At that time, I was also planning to have a way to allow
other programs (for example, a modified version of Turtle) to use
friendly-traceback but also add its own exceptions with its own set
of translations. However, when using gettext in the way described above,
the function ``_`` is added to the Python builtins and points to a single
source for the catalogs.

There is a different way to use gettext to deal with these situations.
I plan to do this. It could happen that I have already done this with the
code but not updated the information in this file.
If you notice that this is the case, feel free to file an issue.


.. warning::

    Using gettext with the default `_` as a builtin clashes with
    an interactive console where `_` is redefined.
