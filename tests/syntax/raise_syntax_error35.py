"""Should raise SyntaxError: name 'x' is parameter and global
"""


def f(x):
    global x
