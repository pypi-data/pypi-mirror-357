from pdfriend.classes.config import Config


def _log_import_error(name: str, e: Exception):
    Config.Logger.warning(f"Failed to initialize command \"{name}\": {e}")


class _BrokenFunc:
    def __init__(self, name: str, e: Exception):
        self._name = name
        self._e = e

    def __call__(self, *args, **kwargs):
        raise ImportError(f"Cannot use command \"{self._name}\": {self._e}")


# We try to be fault tolerant in case something goes really bad
# in the initialization code of any of the commands. The commands
# are independent of each other so you can use the rest even if
# some won't work

try:
    from pdfriend.commands.version import version
except Exception as e:
    _log_import_error("version", e)
    version = _BrokenFunc("version", e)

try:
    from pdfriend.commands.merge import merge
except Exception as e:
    _log_import_error("merge", e)
    merge = _BrokenFunc("merge", e)

try:
    from pdfriend.commands.invert import invert
except Exception as e:
    _log_import_error("invert", e)
    invert = _BrokenFunc("invert", e)

try:
    from pdfriend.commands.edit import edit
except Exception as e:
    _log_import_error("edit", e)
    edit = _BrokenFunc("edit", e)

try:
    from pdfriend.commands.tinker import tinker
except Exception as e:
    _log_import_error("tinker", e)
    tinker = _BrokenFunc("tinker", e)

try:
    from pdfriend.commands.cache import cache
except Exception as e:
    _log_import_error("cache", e)
    cache = _BrokenFunc("cache", e)

try:
    from pdfriend.commands.weave import weave
except Exception as e:
    _log_import_error("weave", e)
    weave = _BrokenFunc("weave", e)

try:
    from pdfriend.commands.split import split
except Exception as e:
    _log_import_error("split", e)
    split = _BrokenFunc("split", e)

try:
    from pdfriend.commands.encrypt import encrypt
except Exception as e:
    _log_import_error("encrypt", e)
    encrypt = _BrokenFunc("encrypt", e)

try:
    from pdfriend.commands.decrypt import decrypt
except Exception as e:
    _log_import_error("decrypt", e)
    decrypt = _BrokenFunc("decrypt", e)

try:
    from pdfriend.commands.metadata import metadata
except Exception as e:
    _log_import_error("metadata", e)
    metadata = _BrokenFunc("metadata", e)

try:
    from pdfriend.commands.get import get
except Exception as e:
    _log_import_error("get", e)
    get = _BrokenFunc("get", e)
