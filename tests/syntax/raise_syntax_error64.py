"""Should raise SyntaxError: duplicate argument 'aa' in function definition"""


def f(aa=1, aa=2):
    pass
