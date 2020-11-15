# friendly-traceback
Aimed at Python beginners: replacing standard traceback by something easier to understand, translatable into various languages.

## Installation

```
pip install friendly-traceback
```

In some terminal console, friendly-traceback can make use of [Rich](https://github.com/willmcgugan/rich) if it is installed; this must be done separately
since Rich is not required for this project, although it is **strongly recommended**
if your terminal console supports it.

## Documentation


[Full documentation available here](https://aroberge.github.io/friendly-traceback-docs/docs/html/)

![Example](https://raw.githubusercontent.com/aroberge/friendly-traceback/master/friendly_indexerror_en.png)


## State of this project

Friendly-traceback is alpha. The current focus is on quickly increasing
the number of exceptions covered.  We strive to test the code as new additions
are made: everything included should work.  However, the code itself
could probably be refactored and could definitely be better documented.

## Contribute

See the documentation. Note that Friendly-traceback uses Black.
![Black logo](https://img.shields.io/badge/code%20style-black-000000.svg)

Some of the ideas were adopted from
[DidYouMean-Python (aka BetterErrorMessages)](https://github.com/SylvainDe/DidYouMean-Python)
by Sylvain Desodt, a project that is also using the MIT license.

## Code of Conduct

We support the
[Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).
Contributors to this project, including those filing or commenting on an issue,
are expected to do the same.

