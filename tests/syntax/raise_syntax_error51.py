"""Should raise SyntaxError: name 's' is assigned to before nonlocal declaration """


def f():
    s = 1

    def g():
        s = 2
        nonlocal s
