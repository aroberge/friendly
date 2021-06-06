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

LANG = "fr"
friendly.install()
friendly.set_lang(LANG)
friendly.set_formatter("docs")

sys.path.insert(0, this_dir)


import trb_syntax_common

target = os.path.normpath(
    os.path.join(docs_root_dir, f"docs/source/syntax_tracebacks_{LANG}.rst")
)

intro_text = """
|france| Friendly SyntaxError tracebacks - en Français
======================================================

Le but principal de friendly est de fournir des rétroactions plus
conviviales que les fameux **tracebacks** de Python lorsqu'une exception survient.
Ci-dessous, on peut voir plusieurs exemples, uniquement pour les
exceptions de type SyntaxError et des classes dérivées;
les autres sont couvertes dans une autre page.
Le but est de documenter ici tous les exemples possibles
tels qu'interprétés par friendly.

.. note::

     Le contenu de cette page a été généré par l'exécution de
     {name} situé dans le répertoire ``tests/``.
     Ceci a besoin d'être fait de manière explicite lorsqu'on veut
     faire des corrections ou des ajouts, avant de faire la mise
     à jour du reste de la documentation avec Sphinx.
     Sous Windows, si Sphinx est installé sur votre ordinateur, il est
     plutôt suggéré d'exécuter make_trb.bat qui est au premier niveau
     du répertoire de fichier. Si vous faites ceci, la documentation pour
     toutes les langues sera automatiquement mise à jour.

Friendly version: {friendly}
Python version: {python}

""".format(
    friendly=friendly.__version__,
    python=platform.python_version(),
    name=__file__,
)

print(f"Python version: {platform.python_version()}; French")

trb_syntax_common.create_tracebacks(target, intro_text)
