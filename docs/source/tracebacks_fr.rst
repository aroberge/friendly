
Friendly tracebacks - en Français
======================================

Le but principal de friendly-traceback est de fournir des rétroactions plus
conviviales que les fameux **tracebacks** de Python lorsqu'une exception survient.
Ci-dessous, on peut voir quelques exemples. Le but éventuel est de documenter
ici tous les exemples possibles tels qu'interprétés par friendly-traceback.

.. note::

     Le contenu de cette page a été généré par l'exécution de
     trb_french.py situé dans le répertoire ``tests/``.
     Ceci a besoin d'être fait de manière explicite lorsqu'on veut
     faire des corrections ou des ajouts, avant de faire la mise
     à jour du reste de la documentation avec Sphinx.
     Sous Windows, si Sphinx est installé sur votre ordinateur, il est
     plutôt suggéré d'exécuter make_trb.bat qui est au premier niveau
     du répertoire de fichier. Si vous faites ceci, la documentation pour
     toutes les langues sera automatiquement mise à jour.

Friendly-traceback version: 0.0.4
Python version: 3.7.0



IndentationError - 1: expected an indented block
------------------------------------------------

.. code-block:: none


    Exception Python: 
        IndentationError: expected an indented block (raise_indentation_error1.py, line 4)

    Une exception de type IndentationError se produit lorsqu'une ligne de code
    n'est pas indentée (c'est-à-dire alignée verticalement avec les autres lignes)
    de la façon attendue.
    Python peut seulement analyser le fichier 'raise_indentation_error1.py'
    jusqu'à l'endroit indiqué par --> et ^.

       1: '''Should raise IndentationError'''
       2: 
       3: if True:
    -->4: pass
             ^

    Cause probable : 
        Dans ce cas-ci, la ligne indiquée ci-dessus par --> devrait
        normalement commencer un nouveau bloc de code indenté.

IndentationError - 2: unexpected indent
---------------------------------------

.. code-block:: none


    Exception Python: 
        IndentationError: unexpected indent (raise_indentation_error2.py, line 4)

    Une exception de type IndentationError se produit lorsqu'une ligne de code
    n'est pas indentée (c'est-à-dire alignée verticalement avec les autres lignes)
    de la façon attendue.
    Python peut seulement analyser le fichier 'raise_indentation_error2.py'
    jusqu'à l'endroit indiqué par --> et ^.

       1: '''Should raise IndentationError'''
       2: if True:
       3:     pass
    -->4:       pass
               ^

    Cause probable : 
        Dans ce cas-ci, la ligne indiquée ci-dessus par -->
        est plus indentée que ce qui était attendu et ne
        correspond pas à l'indentation de la ligne précédente.

IndentationError - 3: unindent does not match ...
-------------------------------------------------

.. code-block:: none


    Exception Python: 
        IndentationError: unindent does not match any outer indentation level (raise_indentation_error3.py, line 4)

    Une exception de type IndentationError se produit lorsqu'une ligne de code
    n'est pas indentée (c'est-à-dire alignée verticalement avec les autres lignes)
    de la façon attendue.
    Python peut seulement analyser le fichier 'raise_indentation_error3.py'
    jusqu'à l'endroit indiqué par --> et ^.

       1: '''Should raise IndentationError'''
       2: if True:
       3:       pass
    -->4:     pass
                  ^

    Cause probable : 
        Dans ce cas-ci, la ligne indiquée ci-dessus par -->
        est moins indentée que la ligne précédente
        et n’est pas alignée verticalement avec un autre bloc de code.

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


    L'exécution s'est arrêtée à la ligne 7 du fichier 'test_name_error.py'

       5: def test_name_error():
       6:     try:
    -->7:         b = c
       8:     except Exception:


SyntaxError
-----------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error1.py, line 3)

    Une exception de type SyntaxError se produit lorsque python ne peut pas comprendre votre code.

    Python peut seulement analyser le fichier 'raise_syntax_error1.py'
    jusqu'à l'endroit indiqué par --> et ^.

       1: """ Should raise SyntaxError"""
       2: 
    -->3: pass = 2
               ^
    Ma meilleure hypothèse: vous essayiez d’assigner une valeur à un mot clé Python.
    Ceci n’est pas permis.


TabError
--------

.. code-block:: none


    Exception Python: 
        TabError: inconsistent use of tabs and spaces in indentation (raise_tab_error.py, line 7)

    Un exception de type TabError indique que vous avez utilisé des espaces ainsi que
    des caractères de tabulation pour indenter votre code.
    Cela n’est pas autorisé dans Python.
    L’indentation de votre code signifie que le bloc de codes est aligné verticalement 
    en insérant des espaces ou des tabulations au début des lignes.
    La recommandation de Python est de toujours utiliser des espaces pour indenter votre code.

    Python peut seulement analyser le fichier 'raise_tab_error.py'
    jusqu'à l'endroit indiqué par --> et ^.

        4: 
        5: def test_tab_error():
        6:     if True:
    --> 7: 	pass
                ^

UnboundLocalError
-----------------

.. code-block:: none


    Exception Python: 
        UnboundLocalError: local variable 'a' referenced before assignment

    En Python, les variables utilisées à l’intérieur d’une fonction sont appelées variables «locales».
    Avant d’utiliser une variable locale, une valeur doit lui être attribuée.
    Une variable utilisée avant l’attribution d’une valeur est supposée être définie en
    dehors de cette fonction; elle est connu comme une variable «globale» ('global' ou parfois 'nonlocal').
    Vous ne pouvez pas assigner une valeur à une telle variable globale à l’intérieur d’une fonction
    sans d’abord confirmer à python qu’il s’agit d’une variable globale, sinon vous verrez
    une exception UnboundLocalError.

    Cause probable : 
        La variable qui semble causer le problème est' a '.
        Essayez d’insérer l’instruction
            global a
        comme première ligne à l’intérieur de votre fonction.

    L'exécution s'est arrêtée à la ligne 13 du fichier 'test_unbound_local_error.py'

       11: 
       12:     try:
    -->13:         inner()
       14:     except Exception:


    Exception levée à la ligne du fichier 'test_unbound_local_error.py'.

        8: 
        9:     def inner():
    -->10:         a += 1
       11: 


Unknown exception
-----------------

.. code-block:: none


    Exception Python: 
        MyException: Some informative message

    Aucune information n'est connue au sujet de cette exception.


    L'exécution s'est arrêtée à la ligne 11 du fichier 'test_unknown_error.py'

        9: def test_unknown_error():
       10:     try:
    -->11:         raise MyException("Some informative message")
       12:     except Exception:


ZeroDivisionError - 1
---------------------

.. code-block:: none


    Exception Python: 
        ZeroDivisionError: division by zero

    Une exception de type ZeroDivisionError se produit lorsque
    vous tentez de diviser une valeur par zéro:
        résultat = ma_variable / 0
    Ceci peut également se produire si vous calculez le reste d’une division 
    à l’aide de l’opérateur modulo '%'
        résultat = ma_variable % 0

    L'exécution s'est arrêtée à la ligne 7 du fichier 'test_zero_division_error.py'

       5: def test_zero_division_error():
       6:     try:
    -->7:         1 / 0
       8:     except Exception:


ZeroDivisionError - 2
---------------------

.. code-block:: none


    Exception Python: 
        ZeroDivisionError: integer division or modulo by zero

    Une exception de type ZeroDivisionError se produit lorsque
    vous tentez de diviser une valeur par zéro:
        résultat = ma_variable / 0
    Ceci peut également se produire si vous calculez le reste d’une division 
    à l’aide de l’opérateur modulo '%'
        résultat = ma_variable % 0

    L'exécution s'est arrêtée à la ligne 17 du fichier 'test_zero_division_error.py'

       15: def test_zero_division_error2():
       16:     try:
    -->17:         1 % 0
       18:     except Exception:

