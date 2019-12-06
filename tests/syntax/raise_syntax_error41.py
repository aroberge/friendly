"""Should raise
Python < 3.8: SyntaxError: keyword can't be an expression
Python 3.8:  expression cannot contain assignment, perhaps you meant "=="?
"""

a = dict('key'=1)
