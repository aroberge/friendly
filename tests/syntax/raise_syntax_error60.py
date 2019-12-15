"""Should raise SyntaxError: name 'x' is parameter and nonlocal"""


def f(x):
    nonlocal x
