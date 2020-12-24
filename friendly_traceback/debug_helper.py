"""Debug helper

The purpose of this file is to help during development.

The idea is to silence internal exceptions raised by Friendly-traceback
itself for most users by redirecting them here, and have them
printed only when debugging mode is activated.
"""

# DEBUG can also be set to True from __main__ or when
# using the debug() command in the console.

DEBUG = r"Users\andre\github\friendly-traceback" in __file__


def log(text):
    if DEBUG:
        print(text)
