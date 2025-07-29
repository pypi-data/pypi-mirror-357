from functools import partial


def lazy_read_property(func):
    """
    A decorator that creates a lazy read-only property for a class. It caches the value upon first access.
    This is similar to `@property` but only evaluates the value once and then saves it for reuse.
    """
    name = "_lazy_" + func.__name__

    @property
    def lazy(self):
        """
        The lazy property which checks if the value exists, if not, computes the value using the provided function (`func`) and saves it for future use.
        """
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value

    return lazy


def wrapper_method(fn=None, hook_cls=None):
    """ """
    if fn is None:
        return partial(wrapper_method, hook_cls=hook_cls)

    def inner(self, *args, **kwargs):
        """ """
        if not hook_cls:
            return fn(*args, **kwargs)
        vd = hook_cls(fn, self)
        return vd(self, *args, **kwargs)

    return inner
