"""Should raise SyntaxError: can't [cannot] assign to conditional expression"""

a if 1 else b = 1
