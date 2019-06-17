from . import patch_pyshell  # noqa

try:
    patch_pyshell.main()
except Exception as e:
    print(e)
    input("ok")
