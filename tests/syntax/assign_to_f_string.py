"""Should raise
Python < 3.8: SyntaxError: can't assign to literal
Python >= 3.8: SyntaxError: cannot assign to f-string expression
"""

f'{x}' = 42
