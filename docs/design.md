# Some thoughts on the design of friendly-traceback

## Basic usage

There should be two ways of using friendly-traceback.

1. As an import hook

```py
import friendly_traceback
friendly_traceback.install()  # sys.excepthook = friendly_traceback.explain
```

2.Catching exceptions locally

```py
try:
    # Some code
except Exception:
    friendly_traceback.explain(*sys.exc_info())
```

By default, friendly tracebacks will be written to sys.stderr.
However, it should be possible to override this choice.

## Localization

It should be possible to translate almost all the text provided.
Some exceptions and examples will be given below.

The determination of which language is used to provide translations
is normally determined by using Python's `locale.getdefaultlocale()`.
However, it can be over-ridden in the following way, in order
of precedence:

1. Using `friendly_traceback.set_lang(lang)`
2. Using the environment variable os.environ['FriendlyTracebackLang']
3. Using variables found in a `.friendly_traceback.ini` file

## Verbosity

There should be different levels of verbosity.

### 1. Basic

A basic level would include four parts:

  1. A single line, introduced by _Python Exception:_ showing the **untranslated** information from Python
  2. A section explaining what is normally meant by a given Exception
  3. A section showing the likely cause of the error.

For example, in English:

```txt
Python exception:
    NameError: name 'c' is not defined

Error found in file 'filename.py' on line 4.

   3: a = 1
-->4: b = c
   5: d = 3

A NameError exception indicates that a variable or
function name is not known to Python.
Most often, this is because there is a spelling mistake;
however, sometimes it is because it is used
before being defined or given a value.

Likely cause:
    In your program, the unknown name is 'c'.
```

The corresponding French version:

```txt
Exception Python:
    NameError: name 'c' is not defined

Erreur trouvée dans le fichier 'filename.py' à la ligne 4.

   3: a = 1
-->4: b = c
   5: d = 3

Une exception de type NameError indique que le nom d'une variable
ou d'une fonction utilisée dans votre programme est inconnu par Python.
Le plus souvent, ceci se produit parce que vous faites une faute
d'orthographe dans l'écriture de votre variable ou de votre fonction;
ceci peut également se produire si vous invoquez cette fonction ou utilisez
cette variable sans l'avoir définie auparavant.

Cause probable:
    Dans votre programme, le nom inconnu est 'c'.
```

### 2. Intermediate

In addition to the basic version, an intermediate version might also include some additional
information about known local and global variables and their values,
similar to what is provided by https://github.com/albertz/py_better_exchook

### 3. Advanced

In addition to what would be provided by the intermediate version,
the advanced version would have the normal Python traceback appended at the end.

### Setting the verbosity level

This could be done when using `friendly_traceback` explicitly in the
program, as an option in the calling function.

If no such option is provided, then it should be set either from
the local environment variables (as for the language) or from a global
`.ini` file.

## Extensibility

For projects that have their custom Exceptions, like AvantPy, it should
be possible to add the custom exceptions to those handled by
friendly-traceback.  Perhaps with something like

```py
import friendly_traceback as friendly
from my_project import my_exceptions

friendly.extend(my_exceptions)
friendly.install()
```

## About the likely cause

For some exceptions, such as NameError, it might be easy to find the
original cause and report it in a way that is easy to understand
as shown in the example above. However, that might not be the case
for SyntaxError.  These could normally be found by using pylint
or flake8 before running the code. It should be possible to either
use one of these packages to do this analysis when an error is found,
or to develop a simplified version that focuses on Syntax Errors,
and is designed from the start to provide localized (i.e. translated)
information.

## Additional configuration

It should be possible to add some colours to various parts of the
traceback information; however, this should likely be done only

1. if friendly_traceback is embedded in another application which has
   full control over its display (some terminal emulators might not
   support control characters required for colours - or do so in
   a way that might be counter productive)
2. Based on values found in a `.ini` file.

This additional feature should only be implemented after all other
issues have been dealt with.

## Other similar projects

Many other projects do some enhanced traceback formatting, however
none that we know of aim at

1. making tracebacks easier to understand by beginners
2. translating traceback information.

Still, there is much to learn by looking at what others are doing.
The following is an incomplete list of projects or modules to look at:

- https://docs.python.org/3/library/cgitb.html
- https://github.com/albertz/py_better_exchook/
- https://github.com/Infinidat/infi.traceback
- https://github.com/laurb9/rich-traceback
- http://www.wotevah.com/code/log.py
- https://github.com/ipython/ipython/blob/master/IPython/core/ultratb.py
- https://github.com/patrys/great-justice
