""" This file has originally been copied from
https://github.com/python/cpython/blob/master/Lib/test/test_syntax.py

It might be helpful to go through the history of this file on github
to see how messages might have changed in previous versions...

The way I am using this file is as follows:
0. First I removed all the examples whose message is "invalid syntax"


1. I choose an example from it, running it with Python 3.6, 3.7, 3.8;
2. I add a test based on this example
3. I add a function in analyze_syntax.py that can deal with this test case.
4. I remove the example from this file, and go back to 1.

The goal is to have no examples left...


"""


# From https://github.com/python/cpython/blob/master/Lib/test/test_syntax.py

# Consult the history of this file for alternative versions

"""This module tests SyntaxErrors.

Here's an example of the sort of thing that is tested.

>>> def f(x):
...     global x
Traceback (most recent call last):
SyntaxError: name 'x' is parameter and global

>>> (True := 1)
Traceback (most recent call last):
SyntaxError: cannot use named assignment with True

>>> (__debug__ := 1)
Traceback (most recent call last):
SyntaxError: cannot assign to __debug__

>>> f() = 1
Traceback (most recent call last):
SyntaxError: cannot assign to function call

>>> del f()
Traceback (most recent call last):
SyntaxError: cannot delete function call

>>> a + 1 = 2
Traceback (most recent call last):
SyntaxError: cannot assign to operator

>>> (x for x in x) = 1
Traceback (most recent call last):
SyntaxError: cannot assign to generator expression

>>> 1 = 1
Traceback (most recent call last):
SyntaxError: cannot assign to literal

>>> "abc" = 1
Traceback (most recent call last):
SyntaxError: cannot assign to literal

>>> b"" = 1
Traceback (most recent call last):
SyntaxError: cannot assign to literal

>>> ... = 1
Traceback (most recent call last):
SyntaxError: cannot assign to Ellipsis


>>> (a, "b", c) = (1, 2, 3)
Traceback (most recent call last):
SyntaxError: cannot assign to literal

>>> [a, b, c + 1] = [1, 2, 3]
Traceback (most recent call last):
SyntaxError: cannot assign to operator

>>> a if 1 else b = 1
Traceback (most recent call last):
SyntaxError: cannot assign to conditional expression


From ast_for_arguments():

>>> def f(x, y=1, z):
...     pass
Traceback (most recent call last):
SyntaxError: non-default argument follows default argument


From ast_for_call():

>>> def f(it, *varargs, **kwargs):
...     return list(it)
>>> L = range(10)
>>> f(x for x in L)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> f(x for x in L, 1)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x for x in L, y=1)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x for x in L, *[])
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x for x in L, **{})
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(L, x for x in L)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x for x in L, y for y in L)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x for x in L,)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f((x for x in L), 1)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


>>> f(lambda x: x[0] = 3)
Traceback (most recent call last):
SyntaxError: expression cannot contain assignment, perhaps you meant "=="?

The grammar accepts any test (basically, any expression) in the
keyword slot of a call site.  Test a few different options.

>>> f(x()=2)
Traceback (most recent call last):
SyntaxError: expression cannot contain assignment, perhaps you meant "=="?
>>> f(a or b=1)
Traceback (most recent call last):
SyntaxError: expression cannot contain assignment, perhaps you meant "=="?
>>> f(x.y=1)
Traceback (most recent call last):
SyntaxError: expression cannot contain assignment, perhaps you meant "=="?
>>> f((x)=2)
Traceback (most recent call last):
SyntaxError: expression cannot contain assignment, perhaps you meant "=="?
>>> f(True=2)
Traceback (most recent call last):
SyntaxError: cannot assign to True
>>> f(__debug__=1)
Traceback (most recent call last):
SyntaxError: cannot assign to __debug__


More set_context():

>>> (x for x in x) += 1
Traceback (most recent call last):
SyntaxError: cannot assign to generator expression

>>> f() += 1
Traceback (most recent call last):
SyntaxError: cannot assign to function call

A continue outside loop should not be allowed.

    >>> def foo():
    ...     try:
    ...         pass
    ...     finally:
    ...         continue
    Traceback (most recent call last):
      ...
    SyntaxError: 'continue' not properly in loop

There is one test for a break that is not in a loop.  The compiler
uses a single data structure to keep track of try-finally and loops,
so we need to be sure that a break is actually inside a loop.  If it
isn't, there should be a syntax error.

   >>> try:
   ...     print(1)
   ...     break
   ...     print(2)
   ... finally:
   ...     print(3)
   Traceback (most recent call last):
     ...
   SyntaxError: 'break' outside loop

This raises a SyntaxError, it used to raise a SystemError.
Context for this change can be found on issue #27514

In 2.5 there was a missing exception and an assert was triggered in a debug
build.  The number of blocks must be greater than CO_MAXBLOCKS.  SF #1565514

   >>> while 1:
   ...  while 2:
   ...   while 3:
   ...    while 4:
   ...     while 5:
   ...      while 6:
   ...       while 8:
   ...        while 9:
   ...         while 10:
   ...          while 11:
   ...           while 12:
   ...            while 13:
   ...             while 14:
   ...              while 15:
   ...               while 16:
   ...                while 17:
   ...                 while 18:
   ...                  while 19:
   ...                   while 20:
   ...                    while 21:
   ...                     while 22:
   ...                      break
   Traceback (most recent call last):
     ...
   SyntaxError: too many statically nested blocks

Misuse of the nonlocal and global statement can lead to a few unique syntax errors.

   >>> def f():
   ...     print(x)
   ...     global x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' is used prior to global declaration

   >>> def f():
   ...     x = 1
   ...     global x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' is assigned to before global declaration

   >>> def f(x):
   ...     global x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' is parameter and global

   >>> def f():
   ...     x = 1
   ...     def g():
   ...         print(x)
   ...         nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' is used prior to nonlocal declaration

   >>> def f():
   ...     x = 1
   ...     def g():
   ...         x = 2
   ...         nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' is assigned to before nonlocal declaration

   >>> def f(x):
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' is parameter and nonlocal

   >>> def f():
   ...     global x
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' is nonlocal and global

   >>> def f():
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: no binding for nonlocal 'x' found

From SF bug #1705365
   >>> nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: nonlocal declaration not allowed at module level

From https://bugs.python.org/issue25973
   >>> class A:
   ...     def f(self):
   ...         nonlocal __x
   Traceback (most recent call last):
     ...
   SyntaxError: no binding for nonlocal '_A__x' found


This tests assignment-context; there was a bug in Python 2.5 where compiling
a complex 'if' (one with 'elif') would fail to notice an invalid suite,
leading to spurious errors.

   >>> if 1:
   ...   x() = 1
   ... elif 1:
   ...   pass
   Traceback (most recent call last):
     ...
   SyntaxError: cannot assign to function call

   >>> if 1:
   ...   pass
   ... elif 1:
   ...   x() = 1
   Traceback (most recent call last):
     ...
   SyntaxError: cannot assign to function call

   >>> if 1:
   ...   x() = 1
   ... elif 1:
   ...   pass
   ... else:
   ...   pass
   Traceback (most recent call last):
     ...
   SyntaxError: cannot assign to function call

   >>> if 1:
   ...   pass
   ... elif 1:
   ...   x() = 1
   ... else:
   ...   pass
   Traceback (most recent call last):
     ...
   SyntaxError: cannot assign to function call

   >>> if 1:
   ...   pass
   ... elif 1:
   ...   pass
   ... else:
   ...   x() = 1
   Traceback (most recent call last):
     ...
   SyntaxError: cannot assign to function call


>>> f(a=23, a=234)
Traceback (most recent call last):
   ...
SyntaxError: keyword argument repeated

>>> {1, 2, 3} = 42
Traceback (most recent call last):
SyntaxError: cannot assign to set display

>>> {1: 2, 3: 4} = 42
Traceback (most recent call last):
SyntaxError: cannot assign to dict display

>>> f'{x}' = 42
Traceback (most recent call last):
SyntaxError: cannot assign to f-string expression

>>> f'{x}-{y}' = 42
Traceback (most recent call last):
SyntaxError: cannot assign to f-string expression

Corner-cases that used to fail to raise the correct error:

    >>> def f(*, x=lambda __debug__:0): pass
    Traceback (most recent call last):
    SyntaxError: cannot assign to __debug__

    >>> def f(*args:(lambda __debug__:0)): pass
    Traceback (most recent call last):
    SyntaxError: cannot assign to __debug__

    >>> def f(**kwargs:(lambda __debug__:0)): pass
    Traceback (most recent call last):
    SyntaxError: cannot assign to __debug__

    >>> with (lambda *:0): pass
    Traceback (most recent call last):
    SyntaxError: named arguments must follow bare *

Corner-cases that used to crash:

    >>> def f(**__debug__): pass
    Traceback (most recent call last):
    SyntaxError: cannot assign to __debug__

    >>> def f(*xx, __debug__): pass
    Traceback (most recent call last):
    SyntaxError: cannot assign to __debug__

"""
