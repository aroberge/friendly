"""Should raise SyntaxError: cannot assign to __debug__ in Py 3.8
   and assignment to keyword before."""

__debug__ = 1
