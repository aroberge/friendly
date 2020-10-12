"""Should raise SyntaxError: invalid syntax"""
for i in range(101):
    if False:
        pass
    elif i % 2 = 0:
        print(i)
