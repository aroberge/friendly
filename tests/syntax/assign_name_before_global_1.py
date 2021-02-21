"""Should raise SyntaxError: name 'p' is assigned to prior to global declaration
"""


def fn():
    p = 1
    global p
