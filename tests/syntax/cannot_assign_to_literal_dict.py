"""Should raise SyntaxError:
Python 3.8: cannot assign to dict display
Python 3.6, 3.7: can't assign to literal

 """

{1 : 2, 2 : 4} = 5
