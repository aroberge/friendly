# note that core.py limits the number of names imported via __all__

import sys

valid_version = sys.version_info.major >= 3 and sys.version_info.minor >= 6

if not valid_version:
    print("Python 3.6 or newer is required.")
    sys.exit()

from .core import *  # noqa
from . import invocation  # noqa
