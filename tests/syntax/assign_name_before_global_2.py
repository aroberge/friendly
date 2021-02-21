"""Should raise SyntaxError: name 'r' is used prior to global declaration
"""


def fn():
    print(r)
    global r
