# SyntaxError: annotated name 'x' can't be global
def foo():
    global x
    x:int = 1

x = 0
foo()