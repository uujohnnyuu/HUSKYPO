from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy


class By(AppiumBy):
    pass


class ByAttribute:
    NAMES = [attr for attr in dir(By) if not attr.startswith('__')]
    VALUES = [getattr(By, attr) for attr in NAMES]


class Key:
    V = 'v'
    VA = 'va'
    H = 'h'
    HA = 'ha'


class SwipeAction:
    V = 'v'
    VA = 'va'
    H = 'h'
    HA = 'ha'
