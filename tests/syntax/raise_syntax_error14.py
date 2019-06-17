"""Should raise SyntaxError: invalid syntax for Python < 3.8
   otherwise, SyntaxError: unmatched ')'
"""
a = (1,
    2,
    3, 4,))
b = 3
