import warnings
from functools import wraps

def deprecated_class(cls):
    @wraps(cls)
    def new_init(*args, **kwargs):
        warnings.warn(
            f"{cls.__name__} is deprecated and will be removed in a future version.",
            category=DeprecationWarning,
            stacklevel=2
        )
        return original_init(*args, **kwargs)

    original_init = cls.__init__
    cls.__init__ = new_init
    return cls
