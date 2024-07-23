from importlib.metadata import version

try:
    __version__ = version("cmems_stac")
except Exception:
    __version__ = "9999"
