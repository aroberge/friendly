
Friendly tracebacks - en Français
======================================

Le but principal de friendly-traceback est de fournir des rétroactions plus
conviviales que les fameux **tracebacks** de Python lorsqu'une exception survient.
Ci-dessous, on peut voir quelques exemples. Le but éventuel est de documenter
ici tous les exemples possibles tels qu'interprétés par friendly-traceback.

.. note::

     Le contenu de cette page a été généré par l'exécution de
     tb_french.py situé dans le répertoire ``tests/``.
     Ceci a besoin d'être fait de manière explicite lorsqu'on veut
     faire des corrections ou des ajouts, avant de faire la mise
     à jour du reste de la documentation avec Sphinx.

Friendly-traceback version: 0.0.3
Python version: 3.7.0



IndentationError - 1: expected an indented block
------------------------------------------------

.. code-block:: none


    Exception Python: 
        IndentationError: expected an indented block (raise_indentation_error1.py, line 4)

    Une exception de type IndentationError se produit lorsqu'une ligne de code
    n'est pas indentée (c'est-à-dire alignée verticalement avec les autres lignes)
    de la façon attendue.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_indentation_error1.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: '''Should raise IndentationError'''
       2: 
       3: if True:
    -->4: pass
             ^
        Dans ce cas-ci, la ligne indiquée ci-dessus par --> devrait
        normalement commencer un nouveau bloc de code indenté.


    L'exécution s'est arrêtée à la ligne 46 du fichier 'tb_common.py'

       44:                 make_title(title)
       45:                 try:
    -->46:                     mod = __import__(name)
       47:                     if function is not None:

IndentationError - 2: unexpected indent
---------------------------------------

.. code-block:: none


    Exception Python: 
        IndentationError: unexpected indent (raise_indentation_error2.py, line 4)

    Une exception de type IndentationError se produit lorsqu'une ligne de code
    n'est pas indentée (c'est-à-dire alignée verticalement avec les autres lignes)
    de la façon attendue.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_indentation_error2.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: '''Should raise IndentationError'''
       2: if True:
       3:     pass
    -->4:       pass
               ^
        Dans ce cas-ci, la ligne indiquée ci-dessus par -->
        est plus indentée que ce qui était attendu et ne
        correspond pas à l'indentation de la ligne précédente.


    L'exécution s'est arrêtée à la ligne 46 du fichier 'tb_common.py'

       44:                 make_title(title)
       45:                 try:
    -->46:                     mod = __import__(name)
       47:                     if function is not None:

IndentationError - 3: unindent does not match ...
-------------------------------------------------

.. code-block:: none


    Exception Python: 
        IndentationError: unindent does not match any outer indentation level (raise_indentation_error3.py, line 4)

    Une exception de type IndentationError se produit lorsqu'une ligne de code
    n'est pas indentée (c'est-à-dire alignée verticalement avec les autres lignes)
    de la façon attendue.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_indentation_error3.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: '''Should raise IndentationError'''
       2: if True:
       3:       pass
    -->4:     pass
                  ^
        Dans ce cas-ci, la ligne indiquée ci-dessus par -->
        est moins indentée que la ligne précédente
        et n’est pas alignée verticalement avec un autre bloc de code.


    L'exécution s'est arrêtée à la ligne 46 du fichier 'tb_common.py'

       44:                 make_title(title)
       45:                 try:
    -->46:                     mod = __import__(name)
       47:                     if function is not None:

NameError
---------

.. code-block:: none


    Exception Python: 
        NameError: name 'c' is not defined

    Une exception NameError indique que le nom d'une variable
    ou d'une fonction n'est pas connue par Python.
    Habituellement, ceci indique une simple faute d'orthographe.
    Cependant, cela peut également indiquer que le nom a été
    utilisé avant qu'on ne lui ait associé une valeur.

    Cause probable : 
        Dans votre programme, le nom inconnu est 'c'.


    L'exécution s'est arrêtée à la ligne 48 du fichier 'tb_common.py'

       46:                     mod = __import__(name)
       47:                     if function is not None:
    -->48:                         getattr(mod, function)()
       49:                 except Exception:


    Exception levée à la ligne du fichier 'raise_name_error.py'.

        6:     """Should raise NameError"""
        7:     a = 1
    --> 8:     b = c
        9:     d = 3
