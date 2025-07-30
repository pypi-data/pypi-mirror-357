def get_version():
    from importlib.metadata import version
    return version("gradiv")

__version__ = get_version()

#add import classes