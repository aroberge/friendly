
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

Example::


    Exception Python: 
        IndentationError: expected an indented block (raise_indentation_error1.py, line 4)

    An indentation error occurs when a given line is
    not indented (aligned vertically) as expected.

    Cause probable : 

        Line 4: pass

        File: raise_indentation_error1.py

        In this case, the line identified in the file above
        was expected to begin a new indented block.

    L'exécution s'est arrêtée à la ligne 46 du fichier 'tb_common.py'

       45:                 try:
    -->46:                     mod = __import__(name)
       47:                     if function is not None:

IndentationError - 2: unexpected indent
---------------------------------------

Example::


    Exception Python: 
        IndentationError: unexpected indent (raise_indentation_error2.py, line 4)

    An indentation error occurs when a given line is
    not indented (aligned vertically) as expected.

    Cause probable : 

        Line 4:       pass

        File: raise_indentation_error2.py

        In this case, the line identified in the file above
        is more indented than expected and does not match
        the indentation of the previous line.

    L'exécution s'est arrêtée à la ligne 46 du fichier 'tb_common.py'

       45:                 try:
    -->46:                     mod = __import__(name)
       47:                     if function is not None:

IndentationError - 3: no match ...
----------------------------------

Example::


    Exception Python: 
        IndentationError: unindent does not match any outer indentation level (raise_indentation_error3.py, line 4)

    An indentation error occurs when a given line is
    not indented (aligned vertically) as expected.

    Cause probable : 

        Line 4:     pass

        File: raise_indentation_error3.py

        In this case, the line identified in the file above
        is less indented the preceding one, and is not aligned
        vertically with another block of code.

    L'exécution s'est arrêtée à la ligne 46 du fichier 'tb_common.py'

       45:                 try:
    -->46:                     mod = __import__(name)
       47:                     if function is not None:

NameError
---------

Example::


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

       47:                     if function is not None:
    -->48:                         getattr(mod, function)()
       49:                 except Exception:

    Exception levée dans le fichier 'raise_name_error.py' à la ligne 8.

       7:     a = 1
    -->8:     b = c
       9:     d = 3
