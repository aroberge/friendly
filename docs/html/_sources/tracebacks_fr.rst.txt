
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
     Sous Windows, si Sphinx est installé sur votre ordinateur, il est
     plutôt suggéré d'exécuter make_tb.bat qui est au premier niveau
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


    L'exécution s'est arrêtée à la ligne 52 du fichier 'tb_common.py'

       50:                     mod = __import__(name)
       51:                     if function is not None:
    -->52:                         getattr(mod, function)()
       53:                 except Exception:


    Exception levée à la ligne du fichier 'raise_name_error.py'.

       4: def test():
       5:     """Should raise NameError"""
    -->6:     b = c
       7:     d = 3

SyntaxError
-----------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error1.py, line 3)

    Une exception SyntaxError se produit lorsque python ne peut pas comprendre votre code.
    Il pourrait y avoir plusieurs raisons possibles:
    - un mot-clé peut être mal orthographié;
    - le symbole deux points, :, ou un autre symbole comme (,], etc., pourrait manquer;
    - etc.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_syntax_error1.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: """ Should raise SyntaxError"""
       2: 
    -->3: pass = 2
               ^
        Actuellement, nous ne pouvons pas vous donner plus d’informations
        sur la cause probable de cette erreur.

TabError - 1
------------

.. code-block:: none


    Exception Python: 
        TabError: inconsistent use of tabs and spaces in indentation (<string>, line 3)

    Un exception de type TabError indique que vous avez utilisé des espaces ainsi que
    des caractères de tabulation pour indenter votre code.
    Cela n’est pas autorisé dans Python.
    L’indentation de votre code signifie que le bloc de codes est aligné verticalement 
    en insérant des espaces ou des tabulations au début des lignes.
    La recommandation de Python est de toujours utiliser des espaces pour indenter votre code.

        Malheureusement, aucune information supplémentaire n’est disponible:
        le contenu du fichier '<string>' n’est pas accessible.

TabError - 2
------------

.. code-block:: none


    Exception Python: 
        TabError: inconsistent use of tabs and spaces in indentation (raise_tab_error2.py, line 7)

    Un exception de type TabError indique que vous avez utilisé des espaces ainsi que
    des caractères de tabulation pour indenter votre code.
    Cela n’est pas autorisé dans Python.
    L’indentation de votre code signifie que le bloc de codes est aligné verticalement 
    en insérant des espaces ou des tabulations au début des lignes.
    La recommandation de Python est de toujours utiliser des espaces pour indenter votre code.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_tab_error2.py'
        jusqu'à l'endroit indiqué par --> et ^.

        4: 
        5: def no_pytest_tab_error2():
        6:     if True:
    --> 7: 	pass
        8: 
                ^

Unknown exception
-----------------

.. code-block:: none


    Exception Python: 
        MyException: Some informative message

    Aucune information n'est connue au sujet de cette exception.


    L'exécution s'est arrêtée à la ligne 52 du fichier 'tb_common.py'

       50:                     mod = __import__(name)
       51:                     if function is not None:
    -->52:                         getattr(mod, function)()
       53:                 except Exception:


    Exception levée à la ligne du fichier 'raise_unknown_error.py'.

        6: 
        7: def test():
    --> 8:     raise MyException("Some informative message")
        9: 
