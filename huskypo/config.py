from __future__ import annotations


class Log:
    PRINT = False
    RECORD = False

class Timeout:
    DEFAULT = 30
    RERAISE = True

    @classmethod
    def reraise(cls, switch: bool | None = None):
        return cls.RERAISE if switch is None else switch


class Appium:
    LOCALHOST = 'http://127.0.0.1'
    PORT_4723 = ':4723'
    WD_HUB = '/wd/hub'  # appium 1.0
