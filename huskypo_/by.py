from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy


class By(AppiumBy):
    pass


class ByAttribute:
    NAMES = [attr for attr in dir(By) if not attr.startswith('__')]
    VALUES = [getattr(By, attr) for attr in NAMES]
    VALUES_WITH_NONE = VALUES + [None]

class SwipeAction:

    # 暫時保留舊有
    V = 'v'
    VA = 'va'
    H = 'h'
    HA = 'ha'

    UNDERLINE = '_'

    # main action
    BORDER = 'border'
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'
    FIX = 'fix'

    # absolute or ratio
    ABSOLUTE = 'absolute'
    RATIO = 'ratio'

    # border: The border value should be absolute coordination or screen protion.
    BORDER_ABSOLUTE = BORDER + UNDERLINE + ABSOLUTE
    BORDER_RATIO = BORDER + UNDERLINE + RATIO

    # vertical: The start and end value should be absolute coordibation or screen protion.
    VERTICAL_ABSOLUTE = VERTICAL + UNDERLINE + ABSOLUTE
    VERTICAL_RATIO = VERTICAL + UNDERLINE + RATIO
    
    # horizontal: The start and end value should be absolute coordibation or screen protion.
    HORIZONTAL_ABSOLUTE = HORIZONTAL + UNDERLINE + ABSOLUTE
    HORIZONTAL_RATIO = HORIZONTAL + UNDERLINE + RATIO

    # fix: The fix value should be absolute coordibation or screen protion.
    FIX_ABSOLUTE = FIX + UNDERLINE + ABSOLUTE
    FIX_RATIO = FIX + UNDERLINE + RATIO

    def __init__(self, border: SwipeAction | None, direction: SwipeAction | None, fix: SwipeAction | None):
        if border and border not in [self.BORDER_ABSOLUTE, self.BORDER_RATIO]:
            raise ValueError(f'Border should be in [BORDER_ABSOLUTE, BORDER_RATIO].')
        if direction and direction not in [
            self.VERTICAL_ABSOLUTE, self.VERTICAL_RATIO, self.HORIZONTAL_ABSOLUTE, self.HORIZONTAL_RATIO]:
            raise ValueError(f'Direction should be in [VERTICAL_ABSOLUTE, VERTICAL_RATIO, HORIZONTAL_ABSOLUTE, HORIZONTAL_RATIO].')
        if fix and fix not in [self.FIX_ABSOLUTE, self.FIX_RATIO]:
            raise ValueError(f'Fix should be in [FIX_ABSOLUTE, FIX_RATIO].')
        self.border = border
        self.direction = direction
        self.fix = fix
    
    @property
    def action(self):
        return self.border, self.direction, self.fix

    