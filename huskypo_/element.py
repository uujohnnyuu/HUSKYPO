# TODO selenium 4.0 and appium 2.0 methods.
from __future__ import annotations

import platform
from typing import Any, Literal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from . import logstack
from . import ec_extension as ecex
from .config import Timeout
from .by import ByAttribute
from .swipe import SwipeBy, SwipeAction
from .swipe import SwipeActionSupport as SAS
from .page import Page
from .typing import WebDriver, WebElement, SeleniumWebElement, AppiumWebElement, AppiumWebDriver


class Element:

    def __init__(
            self,
            by: str | None = None,
            value: str | None = None,
            index: int | None = None,
            timeout: int | float | None = None,
            remark: str | None = None):
        """
        Initial Element attributes.

        Args:
        - by: The locator strategy. You can use all `By` methods as `from huskypo import By`.
        - value: The locator value.
        - index:
            - None: Using `find_element` strategy.
            - int: Using `find_elements` with list index strategy.
        - timeout: Element timeout in seconds of explicit wait.
        - remark: Comments convenient for element identification, or logging.

        Usage (without parameter name)::

            # (by, value)
            element = Element(By.ID, 'element_id')

            # (by, value, index):
            element = Element(By.ID, 'element_id', 3)

            # (by, value, remark):
            element = Element(By.ID, 'element_id', 'this is xxx')

            # (by, value, index, timeout):
            element = Element(By.ID, 'element_id', None, 10)

            # (by, value, index, remark):
            element = Element(By.ID, 'element_id', 3, 'this is xxx')

            # (by, value, index, timeout, remark):
            element = Element(By.ID, 'element_id', 3, 10, 'this is xxx')

        """
        # Get driver reference from Page instance attribute _driver by __get__.
        self._driver: WebDriver | None = None

        # (by, value)
        # Allowing `None` to initialize an empty descriptor for dynamic elements.
        if by not in ByAttribute.VALUES_WITH_NONE:
            raise ValueError(f'The locator strategy "{by}" is undefined.')
        if not isinstance(value, (str, type(None))):
            raise TypeError(f'The locator value type should be "str", not "{type(self.value).__name__}".')
        self.by = by
        self.value = value

        # (by, value, index)
        self.index = index
        # (by, value, remark)
        if not isinstance(index, (int, type(None))):
            remark = str(index)
            self.index = None

        # (by, value, index, timeout)
        self.timeout = timeout
        # (by, value, index, remark)
        if not isinstance(timeout, (int, float, type(None))):
            remark = str(timeout)
            self.timeout = None

        # (by, value, index, timeout, remark)
        self.remark = remark
        if remark is None:
            self.remark = f'{self.value}' if self.index is None else f'({self.value})[{self.index}]'

        # Get the final timeout value from wait()
        self._wait_timeout = None

    def __get__(self, instance: Page, owner):
        # Assign the reference of the page _driver to each element _driver.
        # Since it only assigns a reference, rather than the entire WebDriver object,
        # the memory impact is not significant.
        self._driver = instance._driver
        return self

    def __set__(self, instance: Page, value):
        # Setting element attribute values at runtime,
        # typically used for configuring dynamic elements.
        self.__init__(*value)

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @property
    def locator(self) -> tuple[str, str]:
        """
        Return locator (by, value)
        """
        if self.by is None or self.value is None:
            raise ValueError("""'by' and 'value' cannot be None when performing element operations.
                             Please ensure both are provided with valid values.""")
        return (self.by, self.value)

    @property
    def element_timeout(self):
        """
        Initialize element timeout.
        """
        return Timeout.DEFAULT if self.timeout is None else self.timeout

    @property
    def wait_timeout(self):
        """
        Get actual waiting timeout.
        """
        return self._wait_timeout

    def test_attributes(self):
        """
        unit test
        """
        logstack.info(f'driver           : {self.driver}')
        logstack.info(f'by               : {self.by}')
        logstack.info(f'value            : {self.value}')
        logstack.info(f'locator          : {self.locator}')
        logstack.info(f'index            : {self.index}')
        logstack.info(f'timeout          : {self.timeout}')
        logstack.info(f'element_timeout  : {self.element_timeout}')
        logstack.info(f'wait_timeout     : {self.wait_timeout}')
        logstack.info(f'remark           : {self.remark}')
        logstack.info('')

    def find_element(self) -> WebElement:
        """
        Using the traditional find_element method to locate element without any waiting behavior.
        It is recommended for use in situations where no waiting is required,
        such as the Android UiScrollable locator method.
        """
        return self.driver.find_element(*self.locator)

    def wait(self, timeout: int | float | None = None) -> WebDriverWait:
        """
        Selenium and Appium API.
        Packing WebDriverWait(driver, timeout) to accept only the timeout parameter.

        Args:
        - timeout: Maximum time in seconds to wait for the expected condition.
        """
        # self.wait_timeout is used to record the final timeout value.
        # If the function sets a timeout, it takes precedence;
        # otherwise, it defaults to the timeout set for the element.
        self._wait_timeout = self.element_timeout if timeout is None else timeout
        return WebDriverWait(self.driver, self._wait_timeout)

    def find(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None,
    ) -> WebElement | Literal[False]:
        """
        Selenium and Appium API.
        Wait for the element to be `present`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - WebElement: The element is present before timeout.
        - False: The element is still not present after timeout.
        """
        return self.wait_present(timeout, reraise)

    def wait_present(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        Selenium and Appium API.
        Wait for the element to be `present`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - WebElement: The element is present before timeout.
        - False: The element is still not present after timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.presence_of_element_located(self.locator, self.index),
                f'Wait for element {self.remark} to be present timed out after {self._wait_timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_not_present(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium and Appium API.
        Wait for the element to be `NOT present`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become not present.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - True: The element is not present before timeout.
        - False: The element is still present after timeout.
        """
        try:
            self.wait(timeout).until_not(
                ecex.presence_of_element_located(self.locator, self.index),
                f'Wait for element {self.remark} to be not present timed out after {self._wait_timeout} seconds.')
            return True
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_visible(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        Selenium and Appium API.
        Wait for the element to be `visible`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become visible.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - WebElement: The element is visible before timeout.
        - False: The element is still not present or not visible after timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.visibility_of_element_located(self.locator, self.index),
                f'Wait for element {self.remark} to be visible timed out after {self._wait_timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_not_visible(
            self,
            timeout: int | float | None = None,
            present: bool = True,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium and Appium API.
        Wait for the element to be `not visible`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become not visible.
        - present:
            - True: Only accept not visible condition.
            - False: Accept not present as a part of not visible condition.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - True: The element is not visible before the timeout.
        - None: The element is not present before the timeout, and the present parameter is True.
        - False: The element is still visible after the timeout.
        """
        try:
            result = self.wait(timeout).until_not(
                ecex.visibility_of_element_located(self.locator, self.index),
                f'Wait for element {self.remark} to be not visible timed out after {self._wait_timeout} seconds.')
            if result and present:
                return None
            return True
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_clickable(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> WebElement | Literal[False]:
        """
        Selenium and Appium API.
        Wait for the element to be `clickable`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become clickable.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - WebElement: The element is clickable before timeout.
        - False: The element is still not present or not clickable after timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.element_located_to_be_clickable(self.locator, self.index),
                f'Wait for element {self.remark} to be clickable timed out after {self._wait_timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_not_clickable(
            self,
            timeout: int | float | None = None,
            present: bool = True,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium and Appium API.
        Wait for the element to be `not clickable`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become not clickable.
        - present:
            - True: Only accept not clickable as a condition.
            - False: Accept not present as a part of not clickable condition.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - True: The element is not clickable before the timeout.
        - None: The element is not present before the timeout, and the present parameter is True.
        - False: The element is still clickable after the timeout.
        """
        try:
            result = self.wait(timeout).until_not(
                ecex.element_located_to_be_clickable(self.locator, self.index),
                f'Wait for element {self.remark} to be not clickable timed out after {self._wait_timeout} seconds.')
            if result and present:
                return None
            return True
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_selected(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium and Appium API.
        Wait for the element to be `selected`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become selected.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - True: The element is selected before timeout.
        - False: The element is still not present or not selected after timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.element_located_to_be_selected(self.locator, self.index),
                f'Wait for element {self.remark} to be selected timed out after {self._wait_timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_not_selected(
            self,
            timeout: int | float | None = None,
            present: bool = True,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium and Appium API.
        Wait for the element to be `not selected`.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become not selected.
        - present:
            - True: Only accept not selected as a condition.
            - False: Accept not present as a part of not selected condition.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - True: The element is not selected before the timeout.
        - None: The element is not present before the timeout, and the present parameter is True.
        - False: The element is still selected after the timeout.
        """
        try:
            result = self.wait(timeout).until_not(
                ecex.element_located_to_be_selected(self.locator, self.index),
                f'Wait for element {self.remark} to be not selected timed out after {self._wait_timeout} seconds.')
            if result and present:
                return None
            return True
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def is_present(self, timeout: int | float | None = None) -> bool:
        """
        Selenium and Appium API.
        Whether the element is present.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.

        Returns:
        - True: The element is present before timeout.
        - False: The element is still not present after timeout.
        """
        return True if self.wait_present(timeout, False) else False

    def is_visible(self) -> bool:
        """
        Selenium and Appium API.
        Whether the element is visible.
        """
        return self.wait_present(reraise=True).is_displayed()

    def is_enabled(self) -> bool:
        """
        Selenium and Appium API.
        Whether the element is enabled.
        """
        return self.wait_present(reraise=True).is_enabled()

    def is_clickable(self) -> bool:
        """
        Selenium and Appium API.
        Whether the element is clickable.
        """
        element = self.wait_present(reraise=True)
        return element.is_displayed() and element.is_enabled()

    def is_selected(self) -> bool:
        """
        Selenium and Appium API.
        Whether the element is selected.
        """
        return self.wait_present(reraise=True).is_selected()

    @property
    def text(self) -> str:
        """
        Selenium and Appium API.
        The text of the element when it is present.
        """
        return self.wait_present(reraise=True).text

    @property
    def visible_text(self) -> str:
        """
        Selenium and Appium API.
        The text of the element when it is visible.
        """
        return self.wait_visible(reraise=True).text

    @property
    def rect(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        A dictionary with the size and location of the element when it is present.

        Return:
        - We rearrange it as {'x': int, 'y': int, 'width': int, 'height': int}
        """
        rect = self.wait_present(reraise=True).rect
        return {'x': rect['x'], 'y': rect['y'], 'width': rect['width'], 'height': rect['height']}

    @property
    def location(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        The location of the element when it is present in the renderable canvas.

        Return: {'x': int, 'y': int}
        """
        return self.wait_present(reraise=True).location

    @property
    def size(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        The size of the element when it is present.

        Return:
        - we rearrange it to: {'width': int, 'height': int}
        """
        size = self.wait_present(reraise=True).size
        return {'width': size['width'], 'height': size['height']}

    @property
    def border(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        The border of the element when it is present.

        Return: {'left': int, 'right': int, 'top': int, 'bottom': int}
        """
        rect = self.wait_present(reraise=True).rect
        left = rect['x']
        right = rect['x'] + rect['width']
        top = rect['y']
        bottom = rect['y'] + rect['height']
        return {'left': left, 'right': right, 'top': top, 'bottom': bottom}

    @property
    def center(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        The center location of the element when it is present.

        Return: {'x': int, 'y': int}
        """
        rect = self.wait_present(reraise=True).rect
        x = int(rect['x'] + rect['width'] / 2)
        y = int(rect['y'] + rect['height'] / 2)
        return {'x': x, 'y': y}

    def click(self) -> None:
        """
        Selenium and Appium API.
        Click the element when it is clickable.
        """
        self.wait_clickable(reraise=True).click()

    def tap(self, duration: int | None = None) -> None:
        """
        Appium API.
        Tap the center location of the element when it is present.
        When the element is expected to be clickable,
        but it does not behave as anticipated,
        you can use this method to trigger a click.

        Args:
        - duration: length of time to tap, in ms
        """
        center = tuple(self.center.values())
        self.driver.tap([center], duration)

    def app_drag_and_drop(self, target: Element | AppiumWebElement) -> AppiumWebDriver:
        """
        Appium API.
        Drag the origin element to the destination element

        Args:
            target: the element to drag to
        """
        source = self.wait_present(reraise=True)
        if isinstance(target, Element):
            target = target.wait_present(reraise=True)
        return self.driver.drag_and_drop(source, target)

    def app_scroll(self, target: Element | AppiumWebElement, duration: int | None = None) -> AppiumWebDriver:
        """
        Appium API.
        Scrolls from one element to another

        Args:
            target: the element to scroll to (center of element)
            duration: defines speed of scroll action when moving to target.
                Default is 600 ms for W3C spec.
        """
        source = self.wait_present(reraise=True)
        if isinstance(target, Element):
            target = target.wait_present(reraise=True)
        return self.driver.scroll(source, target, duration)

    def is_viewable(self, timeout: int | float | None = None) -> bool:
        """
        Appium API.
        For native iOS and Android,
        access the element status whether it is in view border.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.
        """
        element = self.wait_present(timeout, False)
        return element.is_displayed() if element else False
    
    def swipe_into_view(
            self,
            action: SwipeAction = SAS.BR_VR,
            border: dict | tuple = {'left': 0, 'right': 100, 'top': 0, 'bottom': 100},
            start: int = 75,
            end: int = 25,
            fix: bool | int = False,
            timeout: int | float = 3,
            max_swipe: int = 10,
            max_adjust: int = 2,
            min_distance: int = 100,
            duration: int = 1000
    ) -> Element:
        """
        Appium API.
        For native iOS and Android apps, this function swipes the screen vertically or horizontally
        until the element becomes present(Android) or visible(iOS) within the specified border.

        Args:
        - direction: Use `SwipeAction`, from huskypo import SwipeAction as SA.
            - vertical: `SA.V` or `SA.VA`, where `VA` denotes `vertical and the border uses absolute pixel values`.
            - horizontal: `SA.H` or `SA.HA`, where `HA` denotes `horizontal and the border uses absolute pixel values`.
        - border: The actual border pixel value or a percentage from 0 to 100.
        - start: The start ratio (0 to 100) of the border parameter.
        - end: The end ratio (0 to 100) of the border parameter.
        - fix:
            - True: Uses the `target element's center x or y` as the fixed coordinate when swiping vertically or horizontally.
            - False: Uses the `border center x or y` as the fixed coordinate when swiping vertically or horizontally.
            - int: Assigns an `absolute x or y` as the fixed coordinate when swiping vertically or horizontally.
        - timeout: The maximum time in seconds to wait for the element to become viewable (either present or visible).
        - max_swipe: The maximum number of swipes allowed.
        - max_adjust: The maximum number of adjustments to align all borders of the element with the view border.
        - min_distance: The minimum swipe distance to avoid being mistaken for a click.
        - duration: The duration of the swipe in milliseconds, from start to end.

        Usage::

            from huskypo.by import Key

            # Default scroll down to find the element.
            page.element.swipe_into_view()

            # Scroll up to find the element with an absolute border.
            border = (50, 450, 100, 700)  # You can determine the actual border by the scrollable element.
            page.element.swipe_into_view(Key.VA, border, 20, 80)

            # Scroll right to find the element with a ratio-based border.
            page.element.swipe_into_view(Key.H)

            # Scroll left to find the element with a ratio-based border.
            border = (10, 90, 10, 90)  # (left, right, top, bottom) will be the ratio of the window size.
            page.element.swipe_into_view(Key.H, border, 25, 75)

            # Horizontal scrolling with a fixed "y" coordinate obtained from the target element.
            # This is applicable to iOS. (Element outside the window is present but not visible.)
            page.element.swipe_into_view(Key.HA, border, 80, 20, True)

            # Horizontal scrolling with a fixed "y" coordinate assigned by an absolute pixel value.
            # This is suitable for Android. (Element outside the window is not present.)
            ty = page.another_present_element.center['y']  # Or you can directly assign a value.
            page.element.swipe_into_view(Key.HA, border, 80, 20, ty)

            # Vertical scrolling with a fixed "x" coordinate assigned by an absolute pixel value.
            # This is suitable for Android. (Element outside the window is not present.)
            tx = page.another_present_element.center['x']  # Or you can directly assign a value.
            page.element.swipe_into_view(Key.VA, border, 80, 20, tx)

        Note:
        `min_distance` and `duration` are interdependent;
        the default settings are based on sliding at a rate of 100 pixels per second,
        which has been found to be stable.
        It is advisable not to alter these unless specific conditions necessitate changes.
        """
        # Action
        swipe_action = self.__get_action(action)

        # Get border.
        swipe_border = self.__get_border(swipe_action, border)

        # Determine v or h, and actual swiping range.
        swipe_range = self.__get_range(swipe_action, *swipe_border, start, end, fix)

        # Start swiping and check whether it is viewable in max count of swiping.
        self.__start_swiping(*swipe_range, duration, timeout, max_swipe)

        # Start adjusting when element is viewable.
        self.__start_adjusting_swipe_range(*swipe_border, *swipe_range, max_adjust, min_distance, duration)

        # Return self to re-trigger the element finding process, thereby avoiding staleness issues.
        return self
    
    def flick_into_view(
            self,
            action: SwipeAction = SAS.BR_VR,
            border: dict | tuple = {'left': 0, 'right': 100, 'top': 0, 'bottom': 100},
            start: int = 75,
            end: int = 25,
            fix: bool | int = False,
            timeout: int | float = 3,
            max_swipe: int = 10,
            max_adjust: int = 2,
            min_distance: int = 100
    ) -> Element:
        """
        Appium API.
        For native iOS and Android apps, this function swipes the screen vertically or horizontally
        until the element becomes present(Android) or visible(iOS) within the specified border.

        Args:
        - direction: Use `SwipeAction`, from huskypo import SwipeAction as SA.
            - vertical: `SA.V` or `SA.VA`, where `VA` denotes `vertical and the border uses absolute pixel values`.
            - horizontal: `SA.H` or `SA.HA`, where `HA` denotes `horizontal and the border uses absolute pixel values`.
        - border: The actual border pixel value or a percentage from 0 to 100.
        - start: The start ratio (0 to 100) of the border parameter.
        - end: The end ratio (0 to 100) of the border parameter.
        - fix:
            - True: Uses the `target element's center x or y` as the fixed coordinate when swiping vertically or horizontally.
            - False: Uses the `border center x or y` as the fixed coordinate when swiping vertically or horizontally.
            - int: Assigns an `absolute x or y` as the fixed coordinate when swiping vertically or horizontally.
        - timeout: The maximum time in seconds to wait for the element to become viewable (either present or visible).
        - max_swipe: The maximum number of swipes allowed.
        - max_adjust: The maximum number of adjustments to align all borders of the element with the view border.
        - min_distance: The minimum swipe distance to avoid being mistaken for a click.
        - duration: The duration of the swipe in milliseconds, from start to end.

        Usage::

            from huskypo.by import Key

            # Default scroll down to find the element.
            page.element.swipe_into_view()

            # Scroll up to find the element with an absolute border.
            border = (50, 450, 100, 700)  # You can determine the actual border by the scrollable element.
            page.element.swipe_into_view(Key.VA, border, 20, 80)

            # Scroll right to find the element with a ratio-based border.
            page.element.swipe_into_view(Key.H)

            # Scroll left to find the element with a ratio-based border.
            border = (10, 90, 10, 90)  # (left, right, top, bottom) will be the ratio of the window size.
            page.element.swipe_into_view(Key.H, border, 25, 75)

            # Horizontal scrolling with a fixed "y" coordinate obtained from the target element.
            # This is applicable to iOS. (Element outside the window is present but not visible.)
            page.element.swipe_into_view(Key.HA, border, 80, 20, True)

            # Horizontal scrolling with a fixed "y" coordinate assigned by an absolute pixel value.
            # This is suitable for Android. (Element outside the window is not present.)
            ty = page.another_present_element.center['y']  # Or you can directly assign a value.
            page.element.swipe_into_view(Key.HA, border, 80, 20, ty)

            # Vertical scrolling with a fixed "x" coordinate assigned by an absolute pixel value.
            # This is suitable for Android. (Element outside the window is not present.)
            tx = page.another_present_element.center['x']  # Or you can directly assign a value.
            page.element.swipe_into_view(Key.VA, border, 80, 20, tx)

        Note:
        `min_distance` and `duration` are interdependent;
        the default settings are based on sliding at a rate of 100 pixels per second,
        which has been found to be stable.
        It is advisable not to alter these unless specific conditions necessitate changes.
        """
        # Action
        flick_action = self.__get_action(action)

        # Get border.
        flick_border = self.__get_border(flick_action, border)

        # Determine v or h, and actual swiping range.
        flick_range = self.__get_range(flick_action, *flick_border, start, end, fix)

        # Start swiping and check whether it is viewable in max count of swiping.
        self.__start_flicking(*flick_range, timeout, max_swipe)

        # Start adjusting when element is viewable.
        # TODO Need to check if it is necessary for flicking is too fast.
        self.__start_adjusting_flick_range(*flick_border, *flick_range, max_adjust, min_distance)

        # Return self to re-trigger the element finding process, thereby avoiding staleness issues.
        return self
    
    def __get_action(self, action: SwipeAction):
        if not isinstance(action, SwipeAction):
            raise TypeError(f'"action" type should be "SwipeAction", not "{type(action).__name__}"')
        if action.border is None:
            action.border = SwipeBy.BORDER_RATIO
        if action.direction is None:
            action.direction = SwipeBy.VERTICAL_RATIO
        logstack._logging(f'✅ Swipe action: {action.action}')
        return action
    
    def __get_border(
            self,
            action: SwipeAction,
            border: dict[str, int] | tuple[int, int, int, int]
    ):
        if isinstance(border, dict):
            left, right, top, bottom = border.values()
        elif isinstance(border, tuple):
            left, right, top, bottom = border
        else:
            raise TypeError('Parameter "border" should be dict or tuple.')

        if action.border and (SwipeBy.RATIO in action.border):
            page = Page(self.driver)
            window_left, window_top, window_width, window_height = page.get_window_rect().values()
            left, right = [int(window_left + window_width * x / 100) for x in (left, right)]
            top, bottom = [int(window_top + window_height * y / 100) for y in (top, bottom)]

        border = (left, right, top, bottom)
        logstack._logging(f'✅ Swipe border: {border}')
        return border

    def __get_range(
            self,
            action: SwipeAction,
            left: int,
            right: int,
            top: int,
            bottom: int,
            start: int,
            end: int,
            fix: bool | int = False
    ):
        width = right - left
        height = bottom - top

        sx = sy = start
        ex = ey = end
        if SwipeBy.VERTICAL in action.direction:
            if SwipeBy.RATIO in action.direction:
                sy = top + int(height * start / 100)
                ey = top + int(height * end / 100)
                # border center x
                sx = ex = left + int(width / 2)
            if fix is True:
                # element center x
                sx = ex = self.center['x']
            elif isinstance(fix, int):
                # absolute x
                sx = ex = fix
                if action.fix and (SwipeBy.RATIO in action.fix):
                    # ratio x
                    sx = ex = left + int(width * fix / 100)
            else:
                raise TypeError('Parameter "fix" should be bool or int.')
        if SwipeBy.HORIZONTAL in action.direction:
            if SwipeBy.RATIO in action.direction:
                sx = left + int(width * start / 100)
                ex = left + int(width * end / 100)
                # border center y
                sy = ey = top + int(height / 2)    
            if fix is True:
                # element center y
                sy = ey = self.center['y']
            elif isinstance(fix, int):
                # absolute y
                sy = ey = fix
                if action.fix and (SwipeBy.RATIO in action.fix):
                    # ratio y
                    sy = ey = top + int(height * fix / 100)
            else:
                raise TypeError('Parameter "fix" should be bool or int.')

        range = (sx, sy, ex, ey)
        logstack._logging(f'✅ Swipe range: {range}')
        return range

    def __start_swiping(
            self,
            sx: int,
            sy: int,
            ex: int,
            ey: int,
            duration: int,
            timeout: int | float,
            max_swipe: int
    ):
        logstack._logging(f'🟢 Start swiping to element {self.remark}.')
        count = 0
        while not self.is_viewable(timeout):
            if count == max_swipe:
                raise ValueError(f'Stop swiping to element {self.remark} as the maximum swipe count of {max_swipe} has been reached.')
            self.driver.swipe(sx, sy, ex, ey, duration)
            count += 1
        logstack._logging(f'✅ End swiping as the element {self.remark} is now viewable.')
        return True
    
    def __start_flicking(
            self,
            sx: int,
            sy: int,
            ex: int,
            ey: int,
            timeout: int | float,
            max_swipe: int
    ):
        logstack._logging(f'🟢 Start flicking to element {self.remark}.')
        count = 0
        while not self.is_viewable(timeout):
            if count == max_swipe:
                raise ValueError(f'Stop flicking to element {self.remark} as the maximum flick count of {max_swipe} has been reached.')
            self.driver.flick(sx, sy, ex, ey)
            count += 1
        logstack._logging(f'✅ End flicking as the element {self.remark} is now viewable.')
        return True

    def __start_adjusting_swipe_range(
            self,
            left: int,
            right: int,
            top: int,
            bottom: int,
            sx: int,
            sy: int,
            ex: int,
            ey: int,
            max_adjust: int,
            min_distance: int,
            duration: int
    ):
        logstack._logging(f'🟢 Start adjusting to element {self.remark}')
        for i in range(1, max_adjust + 2):
            element_left, element_right, element_top, element_bottom = self.border.values()
            delta_left = left - element_left
            delta_right = element_right - right
            delta_top = top - element_top
            delta_bottom = element_bottom - bottom
            if delta_left > 0:
                logstack._logging(f'🟢 Adjust {i}: swipe right.')
                adjust_distance = delta_left if delta_left > min_distance else min_distance
                ex = sx + int(adjust_distance)
            elif delta_right > 0:
                logstack._logging(f'🟢 Adjust {i}: swipe left.')
                adjust_distance = delta_right if delta_right > min_distance else min_distance
                ex = sx - int(adjust_distance)
            elif delta_top > 0:
                logstack._logging(f'🟢 Adjust {i}: swipe down.')
                adjust_distance = delta_top if delta_top > min_distance else min_distance
                ey = sy + int(adjust_distance)
            elif delta_bottom > 0:
                logstack._logging(f'🟢 Adjust {i}: swipe up.')
                adjust_distance = delta_bottom if delta_bottom > min_distance else min_distance
                ey = sy - int(adjust_distance)
            else:
                logstack._logging(f'✅ End adjusting as the element {self.remark} border is in view border.')
                return True
            if i == max_adjust + 1:
                logstack._logging(f'🟡 End adjusting to the element {self.remark} as the maximum adjust count of {max_adjust} has been reached.')
                return True
            self.driver.swipe(sx, sy, ex, ey, duration)

    def __start_adjusting_flick_range(
            self,
            left: int,
            right: int,
            top: int,
            bottom: int,
            sx: int,
            sy: int,
            ex: int,
            ey: int,
            max_adjust: int,
            min_distance: int
    ):
        logstack._logging(f'🟢 Start adjusting to element {self.remark}')
        for i in range(1, max_adjust + 2):
            element_left, element_right, element_top, element_bottom = self.border.values()
            delta_left = left - element_left
            delta_right = element_right - right
            delta_top = top - element_top
            delta_bottom = element_bottom - bottom
            if delta_left > 0:
                logstack._logging(f'🟢 Adjust {i}: swipe right.')
                adjust_distance = delta_left if delta_left > min_distance else min_distance
                ex = sx + int(adjust_distance)
            elif delta_right > 0:
                logstack._logging(f'🟢 Adjust {i}: swipe left.')
                adjust_distance = delta_right if delta_right > min_distance else min_distance
                ex = sx - int(adjust_distance)
            elif delta_top > 0:
                logstack._logging(f'🟢 Adjust {i}: swipe down.')
                adjust_distance = delta_top if delta_top > min_distance else min_distance
                ey = sy + int(adjust_distance)
            elif delta_bottom > 0:
                logstack._logging(f'🟢 Adjust {i}: swipe up.')
                adjust_distance = delta_bottom if delta_bottom > min_distance else min_distance
                ey = sy - int(adjust_distance)
            else:
                logstack._logging(f'✅ End adjusting as the element {self.remark} border is in view border.')
                return True
            if i == max_adjust + 1:
                logstack._logging(f'🟡 End adjusting to the element {self.remark} as the maximum adjust count of {max_adjust} has been reached.')
                return True
            self.driver.flick(sx, sy, ex, ey)

    def clear(self) -> WebElement | None:
        """
        Selenium and Appium API.
        Clear the text of the field type element.

        Returns:
        - None: Selenium.
        - WebElement: Appium.
        """
        return self.wait_present(reraise=True).clear()

    def send_keys(
            self,
            *value,
            click: bool = False,
            clear: bool = False
    ) -> WebElement | None:
        """
        Selenium and Appium API.
        Simulates typing into the element.

        Args:
        - value: The texts or keys to typing.
        - click: Whether performing a click before typing.
        - clear: Whether Removing the typed text of the element before typing.
        - click and clear: If both are True, it will click first and then clear the text.

        Returns:
        - None: Selenium
        - WebElement: Appium
        """
        element = self.wait_present(reraise=True)
        if click:
            element.click()
        if clear:
            element.clear()
        return element.send_keys(*value)

    def get_attribute(self, name: Any | str) -> str | dict | None | Any:
        """
        Selenium and Appium API.

        This method will first try to return the value of a property with the
        given name. If a property with that name doesn't exist, it returns the
        value of the attribute with the same name. If there's no attribute with
        that name, `None` is returned.

        Values which are considered truthy, that is equals "true" or "false",
        are returned as booleans.  All other non-`None` values are returned
        as strings.  For attributes or properties which do not exist, `None`
        is returned.

        To obtain the exact value of the attribute or property,
        use :func:`~selenium.webdriver.remote.BaseWebElement.get_dom_attribute` or
        :func:`~selenium.webdriver.remote.BaseWebElement.get_property` methods respectively.

        Args:
        - name: Name of the attribute/property to retrieve.

        Usage::

            # Check if the "active" CSS class is applied to an element.
            is_active = "active" in target_element.get_attribute("class")

        """
        return self.wait_present(reraise=True).get_attribute(name)

    def get_property(self, name: Any) -> WebElement | bool | dict | str | Any:
        """
        Selenium and Appium API.
        Gets the given property of the element.

        Args:
        - name: Name of the property to retrieve.

        Usage::

            text_length = target_element.get_property("text_length")

        """
        return self.wait_present(reraise=True).get_property(name)

    def submit(self) -> None:
        """
        Selenium API.
        Submits a form.
        """
        self.wait_present(reraise=True).submit()

    @property
    def tag_name(self) -> str:
        """
        Selenium API.
        This element's `tagName` property.
        """
        return self.wait_present(reraise=True).tag_name

    def value_of_css_property(self, property_name: Any) -> str:
        """
        Selenium API.
        The value of a CSS property.
        """
        return self.wait_present(reraise=True).value_of_css_property(property_name)

    def switch_to_frame(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium API.
        Switches focus to the specified frame by webelement.
        """
        try:
            return self.wait(timeout).until(
                ec.frame_to_be_available_and_switch_to_it(self.locator),
                f'Wait for frame by element {self.remark} to be available timed out after {self._wait_timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False
        
    def action_click(self) -> None:
        """
        Selenium ActionChains API.
        Clicks an element.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).click(element).perform()

    def click_and_hold(self) -> None:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on an element.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).click_and_hold(element).perform()
    
    def context_click(self) -> None:
        """
        Selenium ActionChains API.
        Performs a context-click (right click) on an element.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).context_click(element).perform()

    def double_click(self) -> None:
        """
        Selenium ActionChains API.
        Double-clicks an element.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).double_click(element).perform()

    def drag_and_drop(self, target: Element | SeleniumWebElement) -> None:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on the source element, then moves
        to the target element and releases the mouse button.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        source = self.wait_present(reraise=True)
        if isinstance(target, Element):
            target = target.wait_present(reraise=True)
        ActionChains(self.driver).drag_and_drop(source, target).perform()

    def drag_and_drop_by_offset(self, xoffset: int, yoffset: int) -> None:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on the source element,
        then moves to the target offset and releases the mouse button.

        Args:
        - xoffset: X offset to move to.
        - yoffset: Y offset to move to.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).drag_and_drop_by_offset(element, xoffset, yoffset).perform()

    def move_to_element(self) -> None:
        """
        Selenium ActionChains API.
        Moving the mouse to the middle of an element.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).move_to_element(element).perform()

    def move_to_element_with_offset(self, xoffset: int, yoffset: int) -> None:
        """
        Selenium ActionChains API.
        Move the mouse by an offset of the specified element.
        Offsets are relative to the in-view center point of the element.

        Args:
        - xoffset: X offset to move to, as a positive or negative integer.
        - yoffset: Y offset to move to, as a positive or negative integer.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).move_to_element_with_offset(element, xoffset, yoffset).perform()

    def release(self) -> None:
        """
        Selenium ActionChains API.
        Releasing a held mouse button on an element.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).release(element).perform()

    def send_keys_to_element(self, *keys_to_send: str) -> None:
        """
        Selenium ActionChains API.
        Sends keys to an element.

        Args:
        - keys_to_send: The keys to send. Modifier keys constants can be found in the 'Keys' class.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).send_keys_to_element(element, *keys_to_send).perform()

    def scroll_to_element(self) -> None:
        """
        Selenium API.
        If the element is outside the viewport,
        scrolls the bottom of the element to the bottom of the viewport.

        If you want to execute sequential ActionChains operations,
        you can call `page.action` or `your_page.action`, 
        which is an instance of ActionChains, 
        and then chain it with the original ActionChains methods.
        """
        element = self.wait_present(reraise=True)
        ActionChains(self.driver).scroll_to_element(element).perform()

    @property
    def options(self) -> list[SeleniumWebElement]:
        """
        Selenium Select API.
        Returns a list of all options belonging to this select tag.
        """
        element = self.wait_present(reraise=True)
        return Select(element).options
    
    @property
    def all_selected_options(self) -> list[SeleniumWebElement]:
        """
        Selenium Select API.
        Returns a list of all selected options belonging to this select tag.
        """
        element = self.wait_present(reraise=True)
        return Select(element).all_selected_options

    @property
    def first_selected_option(self) -> SeleniumWebElement:
        """
        Selenium Select API.
        The first selected option in this select tag (or the currently selected option in a normal select)
        """
        element = self.wait_present(reraise=True)
        return Select(element).first_selected_option

    def select_by_value(self, value: str) -> None:
        """
        Selenium Select API.
        Select all options that have a value matching the argument.

        That is, when given "foo" this would select an option like:
        <option value="foo">Bar</option>

        Args:
        - value: The value to match against
        """
        element = self.wait_present(reraise=True)
        Select(element).select_by_value(value)

    def select_by_index(self, index: int) -> None:
        """
        Selenium API.
        Select the option at the given index.

        This is done by examining the "index" attribute of an element, and not merely by counting.

        :Args:
        index - The option at this index will be selected
        throws NoSuchElementException If there is no option with specified index in SELECT
        """
        element = self.wait_present(reraise=True)
        Select(element).select_by_index(index)

    def select_by_visible_text(self, text: str) -> None:
        """
        Selenium API.
        Select all options that display text matching the argument.

        That is, when given "Bar" this would select an option like:
        <option value="foo">Bar</option>

        :Args:
        text - The visible text to match against
        throws NoSuchElementException If there is no option with specified text in SELECT
        """
        element = self.wait_present(reraise=True)
        Select(element).select_by_visible_text(text)

    def deselect_all(self) -> None:
        """
        Selenium Select API.
        Clear all selected entries.
        This is only valid when the SELECT supports multiple selections.
        """
        element = self.wait_present(reraise=True)
        Select(element).deselect_all()

    def deselect_by_value(self, value: str) -> None:
        """
        Selenium Select API.
        Deselect all options that have a value matching the argument. That is, when given "foo" this would deselect an option like:
        <option value="foo">Bar</option>

        Args:
        - value: The value to match against
        """
        element = self.wait_present(reraise=True)
        Select(element).deselect_by_value(value)

    def deselect_by_index(self, index: int) -> None:
        """
        Selenium Select API.
        Deselect the option at the given index. 
        This is done by examining the "index" attribute of an element, 
        and not merely by counting.

        Args:
        - index: The option at this index will be deselected
        """
        element = self.wait_present(reraise=True)
        Select(element).deselect_by_index(index)

    def deselect_by_visible_text(self, text: str) -> None:
        """
        Selenium Select API.
        Deselect all options that display text matching the argument. 
        That is, when given "Bar" this would deselect an option like:
        <option value="foo">Bar</option>

        Args:
        - text: The visible text to match against
        """
        element = self.wait_present(reraise=True)
        Select(element).deselect_by_visible_text(text)

    @property
    def location_in_view(self) -> dict[str, int]:
        """
        Appium API.
        Retrieve the location (coordination) of the element relative to the view when it is present.
        Return: {'x': int, 'y': int}
        """
        return self.wait_present(reraise=True).location_in_view

    def enter(self) -> None:
        """
        Selenium API
        Send keys ENTER to the element.
        """
        self.wait_present(reraise=True).send_keys(Keys.ENTER)

    def select_all(self) -> None:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + A" to the element.
        """
        key_c = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        self.wait_present(reraise=True).send_keys(key_c, "a")

    def cut(self) -> None:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + X" to the element.
        """
        key_c = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        self.wait_present(reraise=True).send_keys(key_c, "x")

    def copy(self) -> None:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + C" to the element.
        """
        key_c = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        self.wait_present(reraise=True).send_keys(key_c, "c")

    def paste(self) -> None:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + V" to the element.
        """
        key_c = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        self.wait_present(reraise=True).send_keys(key_c, "v")

    def backspace(self) -> None:
        """
        Selenium API
        Send keys BACKSPACE to the element.
        """
        self.wait_present(reraise=True).send_keys(Keys.BACKSPACE)

    def delete(self) -> None:
        """
        Selenium API
        Send keys DELETE to the element.
        """
        self.wait_present(reraise=True).send_keys(Keys.DELETE)

    def tab(self) -> None:
        """
        Selenium API
        Send keys TAB to the element.
        """
        self.wait_present(reraise=True).send_keys(Keys.TAB)

    def space(self) -> None:
        """
        Selenium API
        Send keys SPACE to the element.
        """
        self.wait_present(reraise=True).send_keys(Keys.SPACE)