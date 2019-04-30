
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

Friendly-traceback version: 0.0.5
Python version: 3.7.0



ArithmeticError
---------------

.. code-block:: none


    Exception Python: 
        ArithmeticError: 

    ArithmeticError est la classe de base pour les exceptions
    qui sont soulevées pour diverses erreurs arithmétiques.
    Il est inhabituel que vous voyiez cette exception;
    normalement, une exception plus spécifique aurait dû être soulevée.

    L'exécution s'est arrêtée à la ligne 10 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_arithmetic_error.py'

        8:         # Usually, a subclass such as ZeroDivisionError, etc., would
        9:         # likely be raised.
    -->10:         raise ArithmeticError
       11:     except Exception:

ImportError
-----------

.. code-block:: none


    Exception Python: 
        ImportError: cannot import name 'Pi' from 'math' (unknown location)

    Cette exception indique qu’un certain objet n’a pas pu
    être importé à partir d’un module ou d’un paquet. Très souvent, c’est
    parce que le nom de l’objet n’est pas écrit correctement.

    Cause probable : 
        L’objet qui n’a pas pu être importé est 'Pi'.
        Le module ou le paquet d'où il devait être importé
        est 'math'.

    L'exécution s'est arrêtée à la ligne 7 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_import_error.py'

       5: def test_import_error():
       6:     try:
    -->7:         from math import Pi
       8:     except Exception:

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

LookupError
-----------

.. code-block:: none


    Exception Python: 
        LookupError: 

    LookupError est la classe de base pour les exceptions qui sont levées
    lorsqu’une clé ou un index utilisé sur un tableau de correspondance ou une séquence est invalide.
    Elle peut également être levée directement par codecs.lookup().

    L'exécution s'est arrêtée à la ligne 11 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_lookup_error.py'

        9:         # other than possibly codecs.lookup(), which is why we raise
       10:         # it directly here for our example.
    -->11:         raise LookupError
       12:     except Exception:

IndexError - short tuple
------------------------

.. code-block:: none


    Exception Python: 
        IndexError: tuple index out of range

    Un IndexError se produit lorsque vous essayez d’obtenir un élément
    d'une liste, d'un tuple, ou d'un objet similaire (séquence), à l’aide d’un index qui
    n’existe pas; typiquement, c’est parce que l’index que vous donnez
    est plus grand que la longueur de la séquence.
    Rappel: le premier élément d'une séquence est à l'index 0.


    Cause probable : 
        Dans ce cas, la séquence est un tuple.

    L'exécution s'est arrêtée à la ligne 9 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_index_error.py'

        7:     b = [1, 2, 3]
        8:     try:
    --> 9:         print(a[3], b[2])
       10:     except Exception:
    a: (1, 2, 3)
    b: [1, 2, 3]


IndexError - long list
----------------------

.. code-block:: none


    Exception Python: 
        IndexError: list index out of range

    Un IndexError se produit lorsque vous essayez d’obtenir un élément
    d'une liste, d'un tuple, ou d'un objet similaire (séquence), à l’aide d’un index qui
    n’existe pas; typiquement, c’est parce que l’index que vous donnez
    est plus grand que la longueur de la séquence.
    Rappel: le premier élément d'une séquence est à l'index 0.


    Cause probable : 
        Dans ce cas, la séquence est une liste.

    L'exécution s'est arrêtée à la ligne 21 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_index_error.py'

       19:     b = tuple(range(50))
       20:     try:
    -->21:         print(a[50], b[0])
       22:     except Exception:
    a: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1... ]  | len(a): 40
    b: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1... )  | len(b): 50


ModuleNotFoundError
-------------------

.. code-block:: none


    Exception Python: 
        ModuleNotFoundError: No module named 'does_not_exist'

    Une exception ModuleNotFoundError indique que vous
    essayez d’importer un module qui ne peut pas être trouvé par Python.
    Cela pourrait être parce que vous fait une faute d'orthographe en écrivant le nom du module
    ou parce qu’il n’est pas installé sur votre ordinateur.

    Cause probable : 
        Dans votre programme, le nom du module inconnu est 'does_not_exist'.

    L'exécution s'est arrêtée à la ligne 7 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_module_not_found_error.py'

       5: def test_module_not_found_error():
       6:     try:
    -->7:         import does_not_exist
       8:     except Exception:

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

    L'exécution s'est arrêtée à la ligne 7 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_name_error.py'

       5: def test_name_error():
       6:     try:
    -->7:         b = c
       8:     except Exception:

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
    L'exécution s'est arrêtée à la ligne 13 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_unbound_local_error.py'

       11: 
       12:     try:
    -->13:         inner()
       14:     except Exception:
    inner: <function test_unbound_local_error.<loca... >

    Exception levée à la ligne du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_unbound_local_error.py'.

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

    L'exécution s'est arrêtée à la ligne 11 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_unknown_error.py'

        9: def test_unknown_error():
       10:     try:
    -->11:         raise MyException("Some informative message")
       12:     except Exception:
    global MyException: <class 'test_unknown_error.MyException'>


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
    L'exécution s'est arrêtée à la ligne 7 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_zero_division_error.py'

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
    L'exécution s'est arrêtée à la ligne 17 du fichier 'C:\Users\andre\github\friendly-traceback\tests\test_zero_division_error.py'

       15: def test_zero_division_error2():
       16:     try:
    -->17:         1 % 0
       18:     except Exception:
