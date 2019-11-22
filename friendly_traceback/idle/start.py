import sys

from . import patch_run  # noqa
from . import patch_pyshell  # noqa

try:
    patch_pyshell.main()
except Exception as e:
    print(e)
    input("ok")

for mod in sys.modules:
    if "run" in mod:
        print(mod)
