
Friendly SyntaxError tracebacks - en Français
=============================================

Le but principal de friendly-traceback est de fournir des rétroactions plus
conviviales que les fameux **tracebacks** de Python lorsqu'une exception survient.
Ci-dessous, on peut voir quelques exemples, uniquement pour les
exceptions de type SyntaxError; les autres sont couvertes dans une autre page.
Le but éventuel est de documenter
ici tous les exemples possibles tels qu'interprétés par friendly-traceback.

.. note::

     Le contenu de cette page a été généré par l'exécution de
     trb_syntax_french.py situé dans le répertoire ``tests/``.
     Ceci a besoin d'être fait de manière explicite lorsqu'on veut
     faire des corrections ou des ajouts, avant de faire la mise
     à jour du reste de la documentation avec Sphinx.
     Sous Windows, si Sphinx est installé sur votre ordinateur, il est
     plutôt suggéré d'exécuter make_tb.bat qui est au premier niveau
     du répertoire de fichier. Si vous faites ceci, la documentation pour
     toutes les langues sera automatiquement mise à jour.

Friendly-traceback version: 0.0.4
Python version: 3.7.0



SyntaxError - Assign to keyword
-------------------------------

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
        Ma meilleure hypothèse: vous essayiez d’assigner une valeur à un mot clé Python.
        Ceci n’est pas permis.


SyntaxError - Missing colon 1
-----------------------------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error2.py, line 3)

    Une exception SyntaxError se produit lorsque python ne peut pas comprendre votre code.
    Il pourrait y avoir plusieurs raisons possibles:
    - un mot-clé peut être mal orthographié;
    - le symbole deux points, :, ou un autre symbole comme (,], etc., pourrait manquer;
    - etc.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_syntax_error2.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: """Should raise SyntaxError"""
       2: 
    -->3: if True
                 ^
        Ma meilleure hypothèse: vous avez écrit un énoncé débutant avec
        'if' mais vous avez oublié d’ajouter deux points ':' à la fin.


SyntaxError - Missing colon 2
-----------------------------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error3.py, line 3)

    Une exception SyntaxError se produit lorsque python ne peut pas comprendre votre code.
    Il pourrait y avoir plusieurs raisons possibles:
    - un mot-clé peut être mal orthographié;
    - le symbole deux points, :, ou un autre symbole comme (,], etc., pourrait manquer;
    - etc.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_syntax_error3.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: """Should raise SyntaxError"""
       2: 
    -->3: while True  # a comment
                                 ^
        Ma meilleure hypothèse: vous vouliez débuter une boucle 'while'
        mais vous avez oublié d’ajouter deux points ':' à la fin.


SyntaxError - elif, not else if
-------------------------------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error4.py, line 5)

    Une exception SyntaxError se produit lorsque python ne peut pas comprendre votre code.
    Il pourrait y avoir plusieurs raisons possibles:
    - un mot-clé peut être mal orthographié;
    - le symbole deux points, :, ou un autre symbole comme (,], etc., pourrait manquer;
    - etc.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_syntax_error4.py'
        jusqu'à l'endroit indiqué par --> et ^.

       2: 
       3: if False:
       4:     pass
    -->5: else if True:
                ^
        Ma meilleure hypothèse: vous avez écrit 'else if'
        au lieu d'utiliser le mot-clé 'elif'.


SyntaxError - elif, not elseif
------------------------------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error5.py, line 5)

    Une exception SyntaxError se produit lorsque python ne peut pas comprendre votre code.
    Il pourrait y avoir plusieurs raisons possibles:
    - un mot-clé peut être mal orthographié;
    - le symbole deux points, :, ou un autre symbole comme (,], etc., pourrait manquer;
    - etc.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_syntax_error5.py'
        jusqu'à l'endroit indiqué par --> et ^.

       2: 
       3: if False:
       4:     pass
    -->5: elseif True:
                    ^
        Ma meilleure hypothèse: vous avez écrit 'elseif'
        au lieu d'utiliser le mot-clé 'elif'.


SyntaxError - malformed def statment - 1
----------------------------------------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error6.py, line 3)

    Une exception SyntaxError se produit lorsque python ne peut pas comprendre votre code.
    Il pourrait y avoir plusieurs raisons possibles:
    - un mot-clé peut être mal orthographié;
    - le symbole deux points, :, ou un autre symbole comme (,], etc., pourrait manquer;
    - etc.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_syntax_error6.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: """Should raise SyntaxError"""
       2: 
    -->3: def :
              ^
        Ma meilleure hypothèse: vous vouliez définir une fonction ou une méthode,
        mais vous avez fait des erreurs de syntaxe.
        La syntaxe correcte est:
            def nom ( arguments_optionnels ) :


SyntaxError - malformed def statment - 2
----------------------------------------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error7.py, line 3)

    Une exception SyntaxError se produit lorsque python ne peut pas comprendre votre code.
    Il pourrait y avoir plusieurs raisons possibles:
    - un mot-clé peut être mal orthographié;
    - le symbole deux points, :, ou un autre symbole comme (,], etc., pourrait manquer;
    - etc.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_syntax_error7.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: """Should raise SyntaxError"""
       2: 
    -->3: def name  :
                    ^
        Ma meilleure hypothèse: vous vouliez définir une fonction ou une méthode,
        mais vous avez fait des erreurs de syntaxe.
        La syntaxe correcte est:
            def nom ( arguments_optionnels ) :


SyntaxError - malformed def statment - 3
----------------------------------------

.. code-block:: none


    Exception Python: 
        SyntaxError: invalid syntax (raise_syntax_error8.py, line 3)

    Une exception SyntaxError se produit lorsque python ne peut pas comprendre votre code.
    Il pourrait y avoir plusieurs raisons possibles:
    - un mot-clé peut être mal orthographié;
    - le symbole deux points, :, ou un autre symbole comme (,], etc., pourrait manquer;
    - etc.

    Cause probable : 
        Python peut seulement analyser le fichier 'raise_syntax_error8.py'
        jusqu'à l'endroit indiqué par --> et ^.

       1: """Should raise SyntaxError"""
       2: 
    -->3: def ( arg )  :
              ^
        Ma meilleure hypothèse: vous vouliez définir une fonction ou une méthode,
        mais vous avez fait des erreurs de syntaxe.
        La syntaxe correcte est:
            def nom ( arguments_optionnels ) :

