# Used with test_verbosity.py

a_1 = 2

def function_1(a):
    a_2 = 4
    a_1 = a_1 + a_2 + a

def function_2(y):
    return function_1(y + 1)


def function_3(x):
    return 3 * function_2(x)

function_3(1)
