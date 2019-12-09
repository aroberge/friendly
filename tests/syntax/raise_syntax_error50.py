"""Should raise SyntaxError: name 'q' is used prior to nonlocal declaration """


def f():
    q = 1

    def g():
        print(q)
        nonlocal q
