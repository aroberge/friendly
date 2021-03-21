__version__ = "0.3.16"


def doc_version():
    """Use this number in the documentation to avoid triggering updates
    of the whole documentation each time the last part of the version is
    changed."""
    parts = __version__.split(".")
    return parts[0] + "." + parts[1]
