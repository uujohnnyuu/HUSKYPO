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
    

class SwipeActionSupport:

    # Generally, fixing is not important as all swipe functions default to half of the full screen size.
    BA_VA = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.VERTICAL_ABSOLUTE)
    BA_VR = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.VERTICAL_RATIO)

    BA_HA = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.HORIZONTAL_ABSOLUTE)
    BA_HR = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.HORIZONTAL_RATIO)

    BR_VA = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.VERTICAL_ABSOLUTE)
    BR_VR = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.VERTICAL_RATIO)

    BR_HA = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.HORIZONTAL_ABSOLUTE)
    BR_HR = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.HORIZONTAL_RATIO)

    # The situation where you need to set 'fix' is when you need to move within a specific range.
    BA_VA_FA = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.VERTICAL_ABSOLUTE, SwipeBy.FIX_ABSOLUTE)
    BA_VA_FR = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.VERTICAL_ABSOLUTE, SwipeBy.FIX_RATIO)

    BA_VR_FA = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.VERTICAL_RATIO, SwipeBy.FIX_ABSOLUTE)
    BA_VR_FR = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.VERTICAL_RATIO, SwipeBy.FIX_RATIO)

    BA_HA_FA = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.HORIZONTAL_ABSOLUTE, SwipeBy.FIX_ABSOLUTE)
    BA_HA_FR = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.HORIZONTAL_ABSOLUTE, SwipeBy.FIX_RATIO)

    BA_HR_FA = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.HORIZONTAL_RATIO, SwipeBy.FIX_ABSOLUTE)
    BA_HR_FR = SwipeAction(SwipeBy.BORDER_ABSOLUTE, SwipeBy.HORIZONTAL_RATIO, SwipeBy.FIX_RATIO)

    BR_VA_FA = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.VERTICAL_ABSOLUTE, SwipeBy.FIX_ABSOLUTE)
    BR_VA_FR = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.VERTICAL_ABSOLUTE, SwipeBy.FIX_RATIO)

    BR_VR_FA = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.VERTICAL_RATIO, SwipeBy.FIX_ABSOLUTE)
    BR_VR_FR = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.VERTICAL_RATIO, SwipeBy.FIX_RATIO)

    BR_HA_FA = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.HORIZONTAL_ABSOLUTE, SwipeBy.FIX_ABSOLUTE)
    BR_HA_FR = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.HORIZONTAL_ABSOLUTE, SwipeBy.FIX_RATIO)

    BR_HR_FA = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.HORIZONTAL_RATIO, SwipeBy.FIX_ABSOLUTE)
    BR_HR_FR = SwipeAction(SwipeBy.BORDER_RATIO, SwipeBy.HORIZONTAL_RATIO, SwipeBy.FIX_RATIO)

    