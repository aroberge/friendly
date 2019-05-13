"""custom_exception_demo.py


   This simulates a user program that triggers various exceptions caught
   by Friendly-traceback; some of the exceptions are custom exceptions
   and one (NameError) is a standard Python exception
"""
import friendly_traceback
import custom_exception

friendly_traceback.install()  # sets up excepthook; used in the very last case


def next_exception(text):
    print("\n\n", "=" * 50)
    input(text)
    print("-" * 50, "\n")


next_exception("Press enter to see the firstexception")
try:
    raise custom_exception.MyException1("A message")  # noqa
except Exception:
    friendly_traceback.explain()


next_exception("Press enter for second exception")
try:
    raise custom_exception.MyException2("Something went wrong", (1, 2, 3))  # noqa
except Exception:
    friendly_traceback.explain()


next_exception("Press enter for third exception")
try:
    raise custom_exception.MyException3("Subclass of SyntaxError", (1, 2, 3))  # noqa
except Exception:
    friendly_traceback.explain()


next_exception("Press enter for fourth exception")
a = 1
try:
    b = a + c  # noqa
except Exception:
    friendly_traceback.explain()


next_exception("Press enter the last exception caught by excepthook")
raise custom_exception.MyException2("A final case", (1, 2, 3))  # noqa
