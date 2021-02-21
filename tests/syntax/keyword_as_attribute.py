"""Should raise SyntaxError: invalid syntax
"""


class A:
    pass


a = A()

a.x = 1
a.pass = 2
