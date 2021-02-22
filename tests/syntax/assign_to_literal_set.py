"""Should raise SyntaxError:
Python 3.8: cannot assign to set display
Python 3.6, 3.7: can't assign to literal

 """

{1, 2, 3} = 4
