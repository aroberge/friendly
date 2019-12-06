"""Should raise SyntaxError: can't assign to function call

Python 3.8: SyntaxError: cannot assign to function call
"""

func(a, b=3) = 4
