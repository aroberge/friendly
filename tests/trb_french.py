"""Creates a version of traceback_fr.rst to insert in the documentation.
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
this_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_dir, ".."))
import friendly


# Make it possible to find docs and tests source
docs_root_dir = os.path.abspath(
    os.path.join(this_dir, "..", "..", "friendly-traceback-docs")
)
assert os.path.isdir(docs_root_dir), "Separate docs repo need to exist"
sys.path.append(os.path.join(this_dir, ".."))


# sys.path.insert(0, root_dir)

LANG = "fr"
friendly.install()
friendly.set_lang(LANG)
friendly.set_formatter("docs")

sys.path.insert(0, this_dir)


import trb_common

target = os.path.normpath(
    os.path.join(docs_root_dir, f"docs/source/tracebacks_{LANG}.rst")
)

intro_text = """
|france| Friendly tracebacks - en Français
===========================================

Le but principal de friendly-traceback est de fournir des rétroactions plus
conviviales que les fameux **tracebacks** de Python lorsqu'une exception survient.
Ci-dessous, on peut voir quelques exemples. Le but éventuel est de documenter
ici tous les exemples possibles tels qu'interprétés par friendly-traceback.

.. note::

     Le contenu de cette page a été généré par l'exécution de
     {name} situé dans le répertoire ``tests/``.
     Ceci a besoin d'être fait de manière explicite lorsqu'on veut
     faire des corrections ou des ajouts, avant de faire la mise
     à jour du reste de la documentation avec Sphinx.

Friendly version: {friendly}
Python version: {python}

""".format(
    friendly=friendly.version.doc_version(),
    python=platform.python_version(),
    name=__file__,
)

print(f"Python version: {platform.python_version()}; French")

trb_common.create_tracebacks(target, intro_text)
