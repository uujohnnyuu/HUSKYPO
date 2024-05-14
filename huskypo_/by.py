from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy


class By(AppiumBy):
    pass


class ByAttribute:
    NAMES = [attr for attr in dir(By) if not attr.startswith('__')]
    VALUES = [getattr(By, attr) for attr in NAMES]
    VALUES_WITH_NONE = VALUES + [None]


class SwipeAction:
    V = 'v'
    VA = 'va'
    H = 'h'
    HA = 'ha'


class _SwipeAction:

    ACTION = {'border': '', 'direction': '', 'fix': ''}

    UNDERLINE = '_'

    # main action
    BORDER = 'border'
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'
    FIX = 'fix'

    # absolute or ratio
    ABSOLUTE = 'absolute'
    RATIO = 'ratio'

    # border
    BORDER_ABSOLUTE = BORDER + UNDERLINE + ABSOLUTE
    BORDER_RATIO = BORDER + UNDERLINE + RATIO

    # vertical
    VERTICAL_ABSOLUTE = VERTICAL + UNDERLINE + ABSOLUTE
    VERTICAL_RATIO = VERTICAL + UNDERLINE + RATIO
    
    # horizontal
    HORIZONTAL_ABSOLUTE = HORIZONTAL + UNDERLINE + ABSOLUTE
    HORIZONTAL_RATIO = HORIZONTAL + UNDERLINE + RATIO

    # fix
    FIX_ABSOLUTE = FIX + UNDERLINE + ABSOLUTE
    FIX_RATIO = FIX + UNDERLINE + RATIO

    # action checker
    @classmethod
    def get_action(cls, action: dict[str, str]):

        ACTION = {'border': '', 'direction': '', 'fix': ''}
        ACTION_KEYS = set(ACTION.keys())
        action_keys = set(action.keys())

        # 檢查更新的Keys是否包含在ACTION當中，並更新ACTION
        if action_keys.issubset(ACTION_KEYS):
            ACTION.update(action)
        else:
            difference_keys = action_keys.difference(ACTION_KEYS)
            raise KeyError(f'''The following keys are not expected: {difference_keys},
                the expected keys are {ACTION_KEYS}.''')
        
        # 賦值檢查
        border, direction, fix = tuple(ACTION.values())
        if border and border not in [cls.BORDER_ABSOLUTE, cls.BORDER_RATIO]:
            raise ValueError(f'Border should be in [BORDER_ABSOLUTE, BORDER_RATIO].')
        if direction and direction not in [cls.VERTICAL_ABSOLUTE, cls.VERTICAL_RATIO, cls.HORIZONTAL_ABSOLUTE, cls.HORIZONTAL_RATIO]:
            raise ValueError(f'Direction should be in [VERTICAL_ABSOLUTE, VERTICAL_RATIO, HORIZONTAL_ABSOLUTE, HORIZONTAL_RATIO].')
        if fix and fix not in [cls.FIX_ABSOLUTE, cls.FIX_RATIO]:
            raise ValueError(f'Fix should be in [FIX_ABSOLUTE, FIX_RATIO].')
        
        return ACTION