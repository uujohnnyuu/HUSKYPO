from huskypo import Element, Elements


def dynamic(func):

    def wrapper(self, *args, **kwargs):
        target = func(self, *args, **kwargs)
        if isinstance(target, (Element, Elements)):
            return target.__get__(self, None)
        raise TypeError("The decorated function must return an Element or Elements instance.")

    return wrapper
