import importlib as _importlib
_importlib.import_module("varv.accessor")

submodules = [
    "io",
    "preprocessing",
    "feature_extraction",
    "classification",
    "events",
    "base",
    "utils",
    "widgets",
]

__all__ = submodules + [
    "__version__",
]

__version__ = "0.0.2"


def __dir__():
    return __all__


def __getattr__(name):
    if name in submodules:
        return _importlib.import_module(f"varv.{name}")
    else:
        try:
            return globals()[name]
        except KeyError:
            raise AttributeError(f"Module 'varv' has no attribute '{name}'")
