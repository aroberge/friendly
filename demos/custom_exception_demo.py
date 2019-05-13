"""custom_exception_test.py"""
import friendly_traceback


from custom_exception import *  # noqa

friendly_traceback.install()  # sets up excepthook; used in the very last case


try:
    raise MyException1("A message")  # noqa
except Exception:
    friendly_traceback.explain()

print("\n\n", "=" * 50)
input("Press enter for second exception")
print("-" * 50, "\n")
try:
    raise MyException2("Something went wrong", (1, 2, 3))  # noqa
except Exception:
    friendly_traceback.explain()

print("\n\n", "=" * 50)
input("Press enter for third exception")
print("-" * 50, "\n")
try:
    raise MyException3("Subclass of SyntaxError", (1, 2, 3))  # noqa
except Exception:
    friendly_traceback.explain()

print("\n\n", "=" * 50)
input("Press enter for fourth exception")
print("-" * 50, "\n")
a = 1
try:
    b = a + c  # noqa
except Exception:
    friendly_traceback.explain()


print("\n\n", "=" * 50)
input("Press enter the last exception caught by excepthook")
print("-" * 50, "\n")
raise MyException2("A final case", (1, 2, 3))  # noqa
