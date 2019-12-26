"""Should raise SyntaxError: no binding for nonlocal 'ab' found"""


def f():
    nonlocal ab
