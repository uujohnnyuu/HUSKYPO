# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

class SwipeBy:
    """
    This class is used to define actions related to swipe methods.
    Basically, you don't need to call any methods here.
    You only need to use the swipe mode you want from SwipeActionType.
    """

    __SEPARATOR = '_'

    BORDER = 'border'
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'
    FIXED = 'fixed'
    LOCATION = 'location'
    PERCENTAGE = 'percentage'

    BL = BORDER + __SEPARATOR + LOCATION
    BP = BORDER + __SEPARATOR + PERCENTAGE

    VL = VERTICAL + __SEPARATOR + LOCATION
    VP = VERTICAL + __SEPARATOR + PERCENTAGE
    
    HL = HORIZONTAL + __SEPARATOR + LOCATION
    HP = HORIZONTAL + __SEPARATOR + PERCENTAGE

    FL = FIXED + __SEPARATOR + LOCATION
    FP = FIXED + __SEPARATOR + PERCENTAGE

class SwipeAction:
    """
    This class is used to package actions of SwipeBy class.
    Basically, you don't need to call any methods here.
    You only need to use the swipe mode you want from SwipeActionType.
    """

    def __init__(self, border: str | None = None, direction: str | None = None, fix: str | None = None):
        if border and border not in [SwipeBy.BL, SwipeBy.BP]:
            raise ValueError(f'Border should be in [SwipeBy.BL, SwipeBy.BP].')
        if direction and direction not in [
            SwipeBy.VL, SwipeBy.VP, SwipeBy.HL, SwipeBy.HP]:
            raise ValueError(f'Direction should be in [SwipeBy.VL, SwipeBy.VP, SwipeBy.HL, SwipeBy.HP].')
        if fix and fix not in [SwipeBy.FL, SwipeBy.FP]:
            raise ValueError(f'Fixed should be in [SwipeBy.FL, SwipeBy.FP].')
        self.border = border
        self.direction = direction
        self.fix = fix
    
    @property
    def action(self):
        return self.border, self.direction, self.fix
    

class SwipeActionType:
    """
    This class is used to create all posiible object of SwipeAction.
    You can get the SwipeAction you want and set it to relative swipe function,
    which contains parameter `action`.

    We set a swipe scenario like:
    - Swipe the page vertically until the element is in view.
    - `border` is location which get by scrollable element.
    - `start=80` and `end=20` are percentage which relative to the border.
    - As above, we should use action `SAT.BL_VP` to perform it.
        - BL: BORDER_LOCATION, which means border value is actual coordinate.
        - VP: VERTICAL_PERCENTAGE, which means swipe range (start and end value) 
            is proportion of border height.

    Usage:: 

        from huskypo import SwipeActionType as SAT

        border = my_page.table_element.border
        my_page.target_element.swipe_into_view(SAT.BL_VP, border, 80, 20)
        
    If you want to confirm the details of action define, please refer to the following:
    - B(BORDER): 
        - Indicates the boundary of the swipe area, we have two type of border:
            - border = {'left': int, 'right': int, 'top': int, 'bottom': int}
            - border = (int, int, int, int) follow by (left, right, top, bottom).
        - You can set the border by assigning numeric or get by scrollable element using
            - border = my_page.scrollable_element.border
    - V(VERTICAL): 
        - Indicates the vertical swipe range within the `border`. 
    - H(HORIZONTAL): 
        - Indicates the horizontal swipe range within the `border`.
    - F(FIXED): 
        - Indicates the fixed position within the `border` during swiping. 
        - For vertical swiping, the x-coordinate is fixed. 
        - For horizontal swiping, the y-coordinate is fixed.
    - L(LOCATION): 
        - Indicates that the swipe-related values are coordinates.
    - P(PERCENTAGE): 
        - Indicates that the swipe-related values are percentages. 
        - The logic is the same as coordinates, with the top-left corner as the origin. 
        - The reference values for the swipe boundaries and swipe ranges differ:
            - B(BORDER): Relative to the percentage of the current page boundary.
            - V(VERTICAL): Relative to the percentage of the border height (height = bottom - top).
            - H(HORIZONTAL): Relative to the percentage of the border width (width = right - left).
            - F(FIXED): Relative to the percentage of the border height or width.
    
    By combining various methods, more precise actions can be defined, such as:
    - BL(BORDER_LOCATION): 
        - Indicates that the border values are coordinates.
    - BP(BORDER_PERCENTAGE): 
        - Indicates that the border values are the proportion of the current page boundary.
    - HP(HORIZONTAL_PERCENTAGE): 
        - Indicates that the horizontal swipe range is a proportion of the border width.
    - VL(VERTICAL_LOCATION): 
        - Indicates that the vertical swipe range is defined by coordinates.
    - FP(FIXED_PERCENTAGE): 
        - Indicates that the fixed position is a proportion of the border height or width.

    For math logic of L(LOCATION) and P(PERCENTAGE), please refer to the following examples:
    - B(BORDER) example:
        - window size: {'width': 200, 'height': 400}
        - border: {'left': 20, 'right': 100, 'top': 0, 'bottom': 90} or (20, 100, 0, 90)
        - BL indicates that the boundary values are coordinates, 
            meaning the swipeable area is a rectangle with x=(20~90) and y=(0~90).
        - BP indicates that the boundary values are proportions of the current page size, 
            meaning the swipeable area is a rectangle with x=200*(20%~100%)=(40~200) and y=400*(0~90%)=(0~360).
    
    - V(VERTICAL) and F(FIXED) example:
        - window size: {'width': 300, 'height': 1000}
        - border: (10, 300, 20, 1000)
        - start: 75
        - end: 25
        - fixed: 50
        - VL indicates that the swipe range values are coordinates, 
            swiping from y=75 to y=25, fixed at x=50 for vertical swiping.
        - VP indicates that the swipe range values are proportions of the border, 
            swiping from y=20+(1000-20)*75%=755 to y=20+(1000-20)*25%=265, 
            fixed at x=10+(300-10)*50%=155 for vertical swiping.
    """

    # Generally, fixing is not important as all swipe functions default to half of the border width or height.
    BL_VL = SwipeAction(SwipeBy.BL, SwipeBy.VL)
    BL_VP = SwipeAction(SwipeBy.BL, SwipeBy.VP)

    BL_HL = SwipeAction(SwipeBy.BL, SwipeBy.HL)
    BL_HP = SwipeAction(SwipeBy.BL, SwipeBy.HP)

    BP_VL = SwipeAction(SwipeBy.BP, SwipeBy.VL)
    BP_VP = SwipeAction(SwipeBy.BP, SwipeBy.VP)

    BP_HL = SwipeAction(SwipeBy.BP, SwipeBy.HL)
    BP_HP = SwipeAction(SwipeBy.BP, SwipeBy.HP)

    # The situation where you need to set 'fixed' is when you need to swipe in a specific range.
    BL_VL_FL = SwipeAction(SwipeBy.BL, SwipeBy.VL, SwipeBy.FL)
    BL_VL_FP = SwipeAction(SwipeBy.BL, SwipeBy.VL, SwipeBy.FP)

    BL_VP_FL = SwipeAction(SwipeBy.BL, SwipeBy.VP, SwipeBy.FL)
    BL_VP_FP = SwipeAction(SwipeBy.BL, SwipeBy.VP, SwipeBy.FP)

    BL_HL_FL = SwipeAction(SwipeBy.BL, SwipeBy.HL, SwipeBy.FL)
    BL_HL_FP = SwipeAction(SwipeBy.BL, SwipeBy.HL, SwipeBy.FP)

    BL_HP_FL = SwipeAction(SwipeBy.BL, SwipeBy.HP, SwipeBy.FL)
    BL_HP_FP = SwipeAction(SwipeBy.BL, SwipeBy.HP, SwipeBy.FP)

    BP_VL_FL = SwipeAction(SwipeBy.BP, SwipeBy.VL, SwipeBy.FL)
    BP_VL_FP = SwipeAction(SwipeBy.BP, SwipeBy.VL, SwipeBy.FP)

    BP_VP_FL = SwipeAction(SwipeBy.BP, SwipeBy.VP, SwipeBy.FL)
    BP_VP_FP = SwipeAction(SwipeBy.BP, SwipeBy.VP, SwipeBy.FP)

    BP_HL_FL = SwipeAction(SwipeBy.BP, SwipeBy.HL, SwipeBy.FL)
    BP_HL_FP = SwipeAction(SwipeBy.BP, SwipeBy.HL, SwipeBy.FP)

    BP_HP_FL = SwipeAction(SwipeBy.BP, SwipeBy.HP, SwipeBy.FL)
    BP_HP_FP = SwipeAction(SwipeBy.BP, SwipeBy.HP, SwipeBy.FP)

    