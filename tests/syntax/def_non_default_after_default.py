"""Should raise SyntaxError: non-default argument follows default argument
"""


def test(a=1, b):
    return a + b
