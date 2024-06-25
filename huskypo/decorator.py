# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

from __future__ import annotations

from . import Element, Elements


def dynamic(func) -> Element | Elements:

    def wrapper(self, *args, **kwargs):
        target = func(self, *args, **kwargs)
        if isinstance(target, (Element, Elements)):
            return target.__get__(self, None)
        raise TypeError("The decorated function must return an Element or Elements instance.")

    return wrapper
