"""Django pagination tools supporting Ajax, multiple and lazy pagination,
Twitter-style and Digg-style pagination.
"""




VERSION = (3, 0, 1)


def get_version():
    """Return the Django EL Pagination version as a string."""
    return '.'.join(map(str, VERSION))
