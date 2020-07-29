"""Should raise SyntaxError: Generator expression must be parenthesized"""
def f(it, *varargs, **kwargs):
    return list(it)

L = range(10)
f(x for x in L, 1)
