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
import friendly_traceback


# Make it possible to find docs and tests source
this_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(this_dir, ".."))

# sys.path.insert(0, root_dir)

LANG = "fr"
friendly_traceback.install()
friendly_traceback.set_lang(LANG)

sys.path.insert(0, this_dir)


import trb_common  # noqa

target = os.path.normpath(os.path.join(root_dir, f"docs/source/tracebacks_{LANG}.rst"))

intro_text = """
Friendly tracebacks - en Français
======================================

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
     Sous Windows, si Sphinx est installé sur votre ordinateur, il est
     plutôt suggéré d'exécuter make_trb.bat qui est au premier niveau
     du répertoire de fichier. Si vous faites ceci, la documentation pour
     toutes les langues sera automatiquement mise à jour.

Friendly-traceback version: {friendly}
Python version: {python}

""".format(
    friendly=friendly_traceback.version.__version__, python=platform.python_version(), name=__file__
)


trb_common.create_tracebacks(target, intro_text)
