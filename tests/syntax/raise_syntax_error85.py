"""Should raise SyntaxError: f-string invalid syntax"""

def test(**k):
    print(f"{**k}")
