"""Should raise SyntaxError:  name 'xy' is nonlocal and global"""

xy = 1


def f():
    global xy
    nonlocal xy
