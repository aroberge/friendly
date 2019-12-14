"""Should raise SyntaxError: can't [cannot] assign to generator expression"""

(x for x in x) = 1
