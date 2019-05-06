"""Creates a version of traceback_en36.rst to insert in the documentation.
"""

# When creating a new translation, you need to:
# 1. Make a copy of this file
# 2. Change the value of LANG as well as 'intro_text' so that they reflect the
#    appropriate language
# 3. Change the first line of this file so that the name of the rst file
#    is correct!


import os
import sys
import platform
import friendly_traceback


# Make it possible to find docs and tests source
this_dir = os.path.dirname(__file__)
docs_root_dir = os.path.abspath(
    os.path.join(this_dir, "..", "..", "friendly-traceback-docs")
)
assert os.path.isdir(docs_root_dir), "Separate docs repo need to exist"

# sys.path.insert(0, root_dir)

LANG = "en"
friendly_traceback.install()
friendly_traceback.set_lang(LANG)

sys.path.insert(0, this_dir)


import trb_common36  # noqa

target = os.path.normpath(
    os.path.join(docs_root_dir, f"docs/source/tracebacks_{LANG}36.rst")
)

intro_text = """
Friendly tracebacks - in English (Python 3.6)
===============================================

Cases for which the information given by Python 3.6 differs from that
given by Python 3.7

Friendly-traceback version: {friendly}
Python version: {python}

""".format(
    friendly=friendly_traceback.version.__version__,
    python=platform.python_version(),
    name=__file__,
)


trb_common36.create_tracebacks(target, intro_text)
