# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

class SwipeBy:
    """
    This class is used to define actions related to swipe methods.
    Basically, you don't need to call any methods here.
    You only need to use the swipe mode you want from SwipeActionMode.
    """

    __SEP = '_'

    BORDER = 'border'
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'
    FIXED = 'fixed'
    COORDINATE = 'coordinate'
    PERCENTAGE = 'percentage'

    BC = BORDER + __SEP + COORDINATE
    BP = BORDER + __SEP + PERCENTAGE

    VC = VERTICAL + __SEP + COORDINATE
    VP = VERTICAL + __SEP + PERCENTAGE
    
    HC = HORIZONTAL + __SEP + COORDINATE
    HP = HORIZONTAL + __SEP + PERCENTAGE

    FC = FIXED + __SEP + COORDINATE
    FP = FIXED + __SEP + PERCENTAGE

class SwipeAction:
    """
    This class is used to package actions of SwipeBy class.
    Basically, you don't need to call any methods here.
    You only need to use the swipe mode you want from SwipeActionMode.
    """

    def __init__(self, border: str | None = None, direction: str | None = None, fixed: str | None = None):
        if border and border not in [SwipeBy.BC, SwipeBy.BP]:
            raise ValueError(f'Border should be in [SwipeBy.BL, SwipeBy.BP].')
        if direction and direction not in [
            SwipeBy.VC, SwipeBy.VP, SwipeBy.HC, SwipeBy.HP]:
            raise ValueError(f'Direction should be in [SwipeBy.VL, SwipeBy.VP, SwipeBy.HL, SwipeBy.HP].')
        if fixed and fixed not in [SwipeBy.FC, SwipeBy.FP]:
            raise ValueError(f'Fixed should be in [SwipeBy.FL, SwipeBy.FP].')
        self.border = border
        self.direction = direction
        self.fixed = fixed
    
    @property
    def action(self):
        return self.border, self.direction, self.fixed
    

class SwipeActionMode:
    """
    This class is used to store all possible objects of SwipeAction. 
    You can get the SwipeAction you want and set it to the relative swipe function, 
    which contains the parameter `action`.

    We set a swipe scenario like:
    - Direction: Swipe the page `vertically` until the element is in the viewport (visible).
    - Border: The `border` value is a location obtained by the scrollable element.
    - Range: The `start=80` and `end=20` value are percentages of the border height,
        which means we will swipe down the page starting from 80% to 20% of the border height.
    
    As above, we should use the action `SAM.BL_VP` to perform it.
    - SAM: `from huskypo import SwipeActionMode as SAM`
    - BL: `Border Location`, which means the border value is an actual coordinate.
    - VP: `Vertical_Percentage`, which means the swipe range (start=80, end=20) 
        is expressed as a percentage of the border height.

    Usage:: 

        from huskypo import SwipeActionMode as SAM

        border = my_page.scrollable_element.border
        my_page.target_element.swipe_into_view(SAM.BL_VP, border, 80, 20)
        
    If you want to confirm the details of action definitions, please refer to the following:

    - B (BORDER): 
        - Indicates the boundary of the swipe area. We have two types of borders:
            - border = `{'left': int, 'right': int, 'top': int, 'bottom': int}`
            - border = `(int, int, int, int)` following the order (left, right, top, bottom).
        - You can set the border by assigning numeric values or obtaining it from:
            - Page: my_page.get_window_border(), which is the default setting in swipe functions. 
            - Element: my_page.scrollable_element.border
    - V (VERTICAL): 
        - Indicates the `start` and `end` value are the vertical swipe range within the border.
    - H (HORIZONTAL): 
        - Indicates the `start` and `end` value are the horizontal swipe range within the border.
    - F (FIXED): 
        - Indicates the fixed position within the border during swiping.
        - For vertical swiping, we will set the x-coordinate to be fixed.
        - For horizontal swiping, we will set the y-coordinate to be fixed.
    - L (LOCATION): 
        - Indicates that the swipe-related values are coordinates.
    - P (PERCENTAGE): 
        - Indicates that the swipe-related values are percentages.
            The logic is the same as coordinates, with the top-left corner as the origin.
        - The reference values for the swipe boundaries and swipe ranges differ:
            - B (BORDER): Relative to the percentage of the current page boundary.
            - V (VERTICAL): Relative to the percentage of the border height (height = bottom - top).
            - H (HORIZONTAL): Relative to the percentage of the border width (width = right - left).
            - F (FIXED): Relative to the percentage of the border height or width.
    
    By combining the above basic actions, more precise actions can be defined, such as:
    - BL (BORDER_LOCATION): 
        - Indicates that the border values are coordinates.
    - BP (BORDER_PERCENTAGE): 
        - Indicates that the border values are the percentages of the current page boundary.
    - HP (HORIZONTAL_PERCENTAGE): 
        - Indicates that the horizontal start and end values are the percentages of the border width.
    - VL (VERTICAL_LOCATION): 
        - Indicates that the vertical start and end values are coordinates.
    - FP (FIXED_PERCENTAGE): 
        - Indicates that the fixed position is the percentage of the border height or width.

    For the mathematical logic of L (LOCATION) and P (PERCENTAGE), please refer to the following examples:
    - B (BORDER) example:
        - window size: {'width': 200, 'height': 400}
        - border: {'left': 20, 'right': 100, 'top': 0, 'bottom': 90} or (20, 100, 0, 90)
        - BL indicates that the boundary values are coordinates,
            meaning the swipeable area is a rectangle with `x=(20~90)` and `y=(0~90)`.
        - BP indicates that the boundary values are proportions of the current page size,
            meaning the swipeable area is a rectangle with `x=200*(20%~100%)=(40~200)` and `y=400*(0~90%)=(0~360)`.
    - V (VERTICAL) and F (FIXED) example:
        - window size: {'width': 300, 'height': 1000}
        - border: (10, 300, 20, 1000)
        - start: 75
        - end: 25
        - fixed: 50
        - VL indicates that the swipe range values are coordinates,
            swiping from `y=75` to `y=25`.
        - FL indicates that the swipe fixed value is coordinate, 
            fixed at `x=50` for vertical swiping.
        - VP indicates that the swipe range values are the percentages of the border,
            swiping from `y=20+(1000-20)*75%=755` to `y=20+(1000-20)*25%=265`,
        - FP indicates that the swipe fixed value is the percentages of the border, 
            fixed at `x=10+(300-10)*50%=155` for vertical swiping.
    """

    # Generally, fixing is not important as all swipe functions default to half of the border width or height.
    BC_VC = SwipeAction(SwipeBy.BC, SwipeBy.VC)
    BC_VP = SwipeAction(SwipeBy.BC, SwipeBy.VP)

    BC_HC = SwipeAction(SwipeBy.BC, SwipeBy.HC)
    BC_HP = SwipeAction(SwipeBy.BC, SwipeBy.HP)

    BP_VC = SwipeAction(SwipeBy.BP, SwipeBy.VC)
    BP_VP = SwipeAction(SwipeBy.BP, SwipeBy.VP)

    BP_HC = SwipeAction(SwipeBy.BP, SwipeBy.HC)
    BP_HP = SwipeAction(SwipeBy.BP, SwipeBy.HP)

    # The situation where you need to set 'fixed' is when you need to swipe in a specific range.
    BC_VC_FC = SwipeAction(SwipeBy.BC, SwipeBy.VC, SwipeBy.FC)
    BC_VC_FP = SwipeAction(SwipeBy.BC, SwipeBy.VC, SwipeBy.FP)

    BC_VP_FC = SwipeAction(SwipeBy.BC, SwipeBy.VP, SwipeBy.FC)
    BC_VP_FP = SwipeAction(SwipeBy.BC, SwipeBy.VP, SwipeBy.FP)

    BC_HC_FC = SwipeAction(SwipeBy.BC, SwipeBy.HC, SwipeBy.FC)
    BC_HC_FP = SwipeAction(SwipeBy.BC, SwipeBy.HC, SwipeBy.FP)

    BC_HP_FC = SwipeAction(SwipeBy.BC, SwipeBy.HP, SwipeBy.FC)
    BC_HP_FP = SwipeAction(SwipeBy.BC, SwipeBy.HP, SwipeBy.FP)

    BP_VC_FC = SwipeAction(SwipeBy.BP, SwipeBy.VC, SwipeBy.FC)
    BP_VC_FP = SwipeAction(SwipeBy.BP, SwipeBy.VC, SwipeBy.FP)

    BP_VP_FC = SwipeAction(SwipeBy.BP, SwipeBy.VP, SwipeBy.FC)
    BP_VP_FP = SwipeAction(SwipeBy.BP, SwipeBy.VP, SwipeBy.FP)

    BP_HC_FC = SwipeAction(SwipeBy.BP, SwipeBy.HC, SwipeBy.FC)
    BP_HC_FP = SwipeAction(SwipeBy.BP, SwipeBy.HC, SwipeBy.FP)

    BP_HP_FC = SwipeAction(SwipeBy.BP, SwipeBy.HP, SwipeBy.FC)
    BP_HP_FP = SwipeAction(SwipeBy.BP, SwipeBy.HP, SwipeBy.FP)