class SwipeBy:
    
    # TODO deprecate.
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

class SwipeAction:

    def __init__(self, border: str | None = None, direction: str | None = None, fix: str | None = None):
        if border and border not in [SwipeBy.BORDER_ABSOLUTE, SwipeBy.BORDER_RATIO]:
            raise ValueError(f'Border should be in [BORDER_ABSOLUTE, BORDER_RATIO].')
        if direction and direction not in [
            SwipeBy.VERTICAL_ABSOLUTE, SwipeBy.VERTICAL_RATIO, SwipeBy.HORIZONTAL_ABSOLUTE, SwipeBy.HORIZONTAL_RATIO]:
            raise ValueError(f'Direction should be in [VERTICAL_ABSOLUTE, VERTICAL_RATIO, HORIZONTAL_ABSOLUTE, HORIZONTAL_RATIO].')
        if fix and fix not in [SwipeBy.FIX_ABSOLUTE, SwipeBy.FIX_RATIO]:
            raise ValueError(f'Fix should be in [FIX_ABSOLUTE, FIX_RATIO].')
        self.border = border
        self.direction = direction
        self.fix = fix
    
    @property
    def action(self):
        return self.border, self.direction, self.fix
    

class SwipeSupport:

    # Border: 2
    # Direction: 2 x 2 = 4
    # Fix: 2
    # Total: 2 x 4 x 2 = 16

    # TODO Define 16 SwipeAction objects.
    pass