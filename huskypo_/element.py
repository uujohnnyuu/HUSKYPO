# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# TODO Keep tracking selenium 4.0 and appium 2.0 new methods.
from __future__ import annotations

import warnings
import math
import platform
from typing import Any, Literal, TypeAlias

from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, InvalidSessionIdException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

from . import logstack
from . import ec_extension as ecex
from .config import Timeout
from .by import ByAttribute
from .page import Page
from .typing import SeleniumWebElement, AppiumWebElement, AppiumWebDriver
from .typing import WebDriver, WebElement

ElementException = (AttributeError, StaleElementReferenceException, InvalidSessionIdException)

IntCoordinate: TypeAlias = dict[str, int] | tuple[int, int, int, int]
FloatCoordinate: TypeAlias = dict[str, float] | tuple[float, float, float, float]
TupleCoordinate: TypeAlias = tuple[int, int, int, int] | tuple[float, float, float, float]
Coordinate: TypeAlias = IntCoordinate | FloatCoordinate

# TODO deprecate
from .by import SwipeAction as SA

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

    def __get__(self, instance: Page, owner):
        """
        Internal use.
        Dynamically obtain the instance of Page and
        execute the corresponding function only when needed.
        """
        self._page = instance
        return self

    def __set__(self, instance: Page, value):
        """
        Internal use.
        Setting element attribute values at runtime,
        typically used for configuring dynamic elements.
        """
        self.__init__(*value)

    @property
    def driver(self) -> WebDriver:
        """
        Get driver from Page.
        """
        return self._page._driver

    @property
    def _action(self) -> ActionChains:
        """
        Internal use.
        Get ActionChains object from Page.
        """
        return self._page._action

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
    def initial_timeout(self):
        """
        Get the initial timeout of the element.
        """
        return Timeout.DEFAULT if self.timeout is None else self.timeout

    def test_attributes(self):
        """
        Unit test.
        You can call this function to check the attributes are expected.
        """
        logstack.info(f'by              : {self.by}')
        logstack.info(f'value           : {self.value}')
        logstack.info(f'locator         : {self.locator}')
        logstack.info(f'index           : {self.index}')
        logstack.info(f'timeout         : {self.timeout}')
        logstack.info(f'initial_timeout : {self.initial_timeout}')
        logstack.info(f'remark          : {self.remark}\n')

    def find_element(self) -> WebElement:
        """
        Using the traditional find_element method 
        to locate element without any waiting behavior.
        It is recommended for use in situations where no waiting is required,
        such as the Android UiScrollable locator method.
        """
        return self.driver.find_element(*self.locator)

    def wait(self, timeout: int | float | None = None) -> WebDriverWait:
        """
        Selenium and Appium API.
        Packing WebDriverWait(driver, timeout) to accept only the timeout parameter.
        If you sets a timeout in here, it takes precedence;
        otherwise, it defaults to the timeout set for the element.

        Args:
        - timeout: Maximum time in seconds to wait for the expected condition.
        """
        self._wait_timeout = self.initial_timeout if timeout is None else timeout
        return WebDriverWait(self.driver, self._wait_timeout)

    @property
    def wait_timeout(self):
        """
        Get the final waiting timeout of the element.
        If no element action has been executed yet,
        it will return None.
        """
        try:
            return self._wait_timeout
        except AttributeError:
            return None

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
    
    @property
    def _mark(self) -> WebElement | tuple[str, str]:
        """
        Internal use.
        Get WebElement if the element is not stale; otherwise, return the locator.
        This will be called in wait_related functions.
        """
        try:
            self._present_element.is_displayed()
            return self._present_element
        except ElementException:
            return self.locator
        
    @property
    def present_element(self) -> WebElement:
        """
        Get WebElement if the element is not stale; 
        otherwise, execute the wait_present to re-find it.
        """
        try:
            self._present_element.is_displayed()
            return self._present_element
        except ElementException:
            return self.wait_present(reraise=True)
        
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
            self._present_element = self.wait(timeout).until(
                ecex.presence_of_element_located(self.locator, self.index),
                f'Wait for element {self.remark} to be present timed out after {self._wait_timeout} seconds.')
            return self._present_element
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
            self._visible_element = self.wait(timeout).until(
                ecex.visibility_of_element(self._mark, self.index),
                f'Wait for element {self.remark} to be visible timed out after {self._wait_timeout} seconds.')
            self._present_element = self._visible_element
            return self._visible_element
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
            This means that you accept only the element to be not visible, 
            but now the element is not present,
            so it will return None as the element status is not as expected.
        - False: The element is still visible after the timeout.
        """
        try:
            result = self.wait(timeout).until_not(
                ecex.visibility_of_element(self._mark, self.index),
                f'Wait for element {self.remark} to be not visible timed out after {self._wait_timeout} seconds.')
            if result and present:
                # result = True means it triggered NoSuchElementException.
                # If present is also True, 
                # we will return None because it does not match the expected state.
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
            self._clickable_element = self.wait(timeout).until(
                ecex.element_to_be_clickable(self._mark, self.index),
                f'Wait for element {self.remark} to be clickable timed out after {self._wait_timeout} seconds.')
            self._present_element = self._visible_element = self._clickable_element
            return self._clickable_element
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
            This means that you accept only the element to be not clickable, 
            but now the element is not present,
            so it will return None as the element status is not as expected.
        - False: The element is still clickable after the timeout.
        """
        try:
            result = self.wait(timeout).until_not(
                ecex.element_to_be_clickable(self._mark, self.index),
                f'Wait for element {self.remark} to be not clickable timed out after {self._wait_timeout} seconds.')
            if result and present:
                # result = True means it triggered NoSuchElementException.
                # If present is also True, 
                # we will return None because it does not match the expected state.
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
                ecex.element_to_be_selected(self._mark, self.index),
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
            This means that you accept only the element to be not selected, 
            but now the element is not present,
            so it will return None as the element status is not as expected.
        - False: The element is still selected after the timeout.
        """
        try:
            result = self.wait(timeout).until_not(
                ecex.element_to_be_selected(self._mark, self.index),
                f'Wait for element {self.remark} to be not selected timed out after {self._wait_timeout} seconds.')
            if result and present:
                # result = True means it triggered NoSuchElementException.
                # If present is also True, 
                # we will return None because it does not match the expected state.
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
        try:
            self._present_element.is_displayed()
            return True
        except ElementException:
            return True if self.wait_present(timeout, False) else False

    def is_visible(self) -> bool:
        """
        Selenium and Appium API.
        Whether the element is visible.
        """
        try:
            return self._present_element.is_displayed()
        except ElementException:
            return self.wait_present(reraise=True).is_displayed()

    def is_enabled(self) -> bool:
        """
        Selenium and Appium API.
        Whether the element is enabled.
        """
        try:
            return self._present_element.is_enabled()
        except ElementException:
            return self.wait_present(reraise=True).is_enabled()

    def is_clickable(self) -> bool:
        """
        Selenium and Appium API.
        Whether the element is clickable.
        """
        try:
            return self._present_element.is_displayed() and self._present_element.is_enabled()
        except ElementException:
            element = self.wait_present(reraise=True)
            return element.is_displayed() and element.is_enabled()

    def is_selected(self) -> bool:
        """
        Selenium and Appium API.
        Whether the element is selected.
        """
        try:
            return self._present_element.is_selected()
        except ElementException:
            return self.wait_present(reraise=True).is_selected()

    @property
    def text(self) -> str:
        """
        Selenium and Appium API.
        The text of the element when it is present.
        """
        try:
            return self._present_element.text
        except ElementException:
            return self.wait_present(reraise=True).text

    @property
    def visible_text(self) -> str:
        """
        Selenium and Appium API.
        The text of the element when it is visible.
        """
        try:
            return self._visible_element.text
        except ElementException:
            return self.wait_visible(reraise=True).text

    @property
    def rect(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        A dictionary with the size and location of the element when it is present.

        Return:
        - We rearrange it as {'x': int, 'y': int, 'width': int, 'height': int}
        """
        try:
            rect = self._present_element.rect
        except ElementException:
            rect = self.wait_present(reraise=True).rect
        return {'x': rect['x'], 'y': rect['y'], 'width': rect['width'], 'height': rect['height']}

    @property
    def location(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        The location of the element when it is present in the renderable canvas.

        Return: {'x': int, 'y': int}
        """
        try:
            return self._present_element.location
        except ElementException:
            return self.wait_present(reraise=True).location

    @property
    def size(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        The size of the element when it is present.

        Return:
        - we rearrange it to: {'width': int, 'height': int}
        """
        try:
            size = self._present_element.size
        except ElementException:
            size = self.wait_present(reraise=True).size
        return {'width': size['width'], 'height': size['height']}

    @property
    def border(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        The border of the element when it is present.

        Return: {'left': int, 'right': int, 'top': int, 'bottom': int}
        """
        try:
            rect = self._present_element.rect
        except ElementException:
            rect = self.wait_present(reraise=True).rect
        left = rect['x']
        right = left + rect['width']
        top = rect['y']
        bottom = top + rect['height']
        return {'left': left, 'right': right, 'top': top, 'bottom': bottom}

    @property
    def center(self) -> dict[str, int]:
        """
        Selenium and Appium API.
        The center location of the element when it is present.

        Return: {'x': int, 'y': int}
        """
        try:
            rect = self._present_element.rect
        except ElementException:
            rect = self.wait_present(reraise=True).rect
        x = int(rect['x'] + rect['width'] / 2)
        y = int(rect['y'] + rect['height'] / 2)
        return {'x': x, 'y': y}

    def click(self) -> None:
        """
        Selenium and Appium API.
        Click the element when it is clickable.
        """
        try:
            self._clickable_element.click()
        except ElementException:
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
        source = self.present_element
        if isinstance(target, Element):
            target = target.present_element
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
        source = self.present_element
        if isinstance(target, Element):
            target = target.present_element
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

    def swipe_by(
        self,
        offset: Coordinate = {'start_x': 0.5, 'start_y': 0.75, 'end_x': 0.5, 'end_y': 0.25},
        area: Coordinate = {'x': 0.0, 'y': 0.0, 'width': 1.0, 'height': 1.0},
        timeout: int | float = 3,
        max_swipe: int = 10,
        max_adjust: int = 2,
        min_distance: int = 100,
        duration: int = 1000
    ) -> Element:
        """
        Appium API.
        For native iOS and Android apps, 
        this function swipes the screen until the element becomes visible
        within the specified area.

        Args:
        - offset: The swiping range, which can be set as:
            - int: The absolute coordinates.
                - dict: {'start_x': int, 'start_y': int, 'end_x': int, 'end_y': int}
                - tuple: (int, int, int, int) corresponding to the keys in the dict.
            - float: The ratio of the border (swipeable range), which should be between 0.0 and 1.0.
                - dict: {'start_x': float, 'start_y': float, 'end_x': float, 'end_y': float}
                - tuple: (float, float, float, float) corresponding to the keys in the dict.
        - area: The swipeable area, default is the current window size, which can be set as:
            - int: The absolute rectangle.
                - dict: {'x': int, 'y': int, 'width': int, 'height': int}
                - tuple: (int, int, int, int) corresponding to the keys in the dict.
            - float: The ratio of the current window size, which should be between 0.0 and 1.0.
                - dict: {'x': float, 'y': float, 'width': float, 'height': float}
                - tuple: (float, float, float, float) corresponding to the keys in the dict.
        - timeout: The maximum time in seconds to wait for the element to become viewable (visible).
        - max_swipe: The maximum number of swipes allowed.
        - max_adjust: The maximum number of adjustments to align all borders of the element within the view border.
        - min_distance: The minimum swipe distance to avoid being mistaken for a click.
        - duration: The duration of the swipe in milliseconds, from start to end.

        Note of Args `min_distance` and `duration`:
        - `min_distance` and `duration` are interdependent.
        - The default settings are based on sliding at a rate of 100 pixels per second,
            which has been found to be stable.
        - It is advisable not to alter these unless specific conditions necessitate changes.

        Usage::

            # Default is swiping up.
            # offset = (0.5, 0.75, 0.5, 0.25) and area = (0.0, 0.0, 1.0, 1.0) means
            # x: Fixed 50% (0.5) of current window width (100% (1.0) window width).
            # y: From 75% (0.75) to 25% (0.25) of current window height (100% (1.0) window height).
            my_page.target_element.swipe_by()

            # Swipe with customize absolute offset.
            # Note that the area parameter will affect the adjusting process.
            # We recommend not setting the area in this case, 
            # unless you have a specific testing scenario.
            # (ex. Swiping range is not within the area, 
            # and the target element should be inside the area after swiping.)
            my_page.target_element.swipe_by((250, 300, 400, 700))

            # Swipe with ratio of area.
            # Area is current window size (default).
            my_page.target_element.swipe_by((0.3, 0.85, 0.5, 0.35))

            # Swipe with ratio of area.
            # Area is ratio of current window size.
            my_page.target_element.swipe_by((0.3, 0.85, 0.5, 0.35), (0.2, 0.2, 0.6, 0.8))

            # Swipe with ratio of area.
            # Area is absolute coordinate.
            my_page.target_element.swipe_by((0.3, 0.85, 0.5, 0.35), (100, 150, 300, 700))

            # Get absolute area coordinate by scrollable element rect.
            area = my_page.scrollable_element.rect
            my_page.target_element.swipe_by((0.3, 0.85, 0.5, 0.35), area)

        """
        area = self.__get_area(area)
        offset = self.__get_offset(offset, area)
        self.__start_swiping_by(offset, duration, timeout, max_swipe)
        self.__start_adjusting_by(offset, area, max_adjust, min_distance, duration)
        return self

    def flick_by(
        self,
        offset: Coordinate = {'start_x': 0.5, 'start_y': 0.75, 'end_x': 0.5, 'end_y': 0.25},
        area: Coordinate = {'x': 0.0, 'y': 0.0, 'width': 1.0, 'height': 1.0},
        timeout: int | float = 3,
        max_flick: int = 10,
        max_adjust: int = 2,
        min_distance: int = 100,
        duration: int = 1000
    ) -> Element:
        """
        Appium API.
        For native iOS and Android apps, 
        this function flicks the screen until the element becomes visible
        within the specified area.

        Args:
        - offset: The swiping range, which can be set as:
            - int: The absolute coordinates.
                - dict: {'start_x': int, 'start_y': int, 'end_x': int, 'end_y': int}
                - tuple: (int, int, int, int) corresponding to the keys in the dict.
            - float: The ratio of the border (swipeable range), which should be between 0.0 and 1.0.
                - dict: {'start_x': float, 'start_y': float, 'end_x': float, 'end_y': float}
                - tuple: (float, float, float, float) corresponding to the keys in the dict.
        - area: The swipeable area, default is the current window size, which can be set as:
            - int: The absolute rectangle.
                - dict: {'x': int, 'y': int, 'width': int, 'height': int}
                - tuple: (int, int, int, int) corresponding to the keys in the dict.
            - float: The ratio of the current window size, which should be between 0.0 and 1.0.
                - dict: {'x': float, 'y': float, 'width': float, 'height': float}
                - tuple: (float, float, float, float) corresponding to the keys in the dict.
        - timeout: The maximum time in seconds to wait for the element to become viewable (visible).
        - max_flick: The maximum number of swipes allowed.
        - max_adjust: The maximum number of adjustments to align all borders of the element within the view border.
        - min_distance: Adjusting. The minimum swipe distance to avoid being mistaken for a click.
        - duration: Adjustung. The duration of the swipe in milliseconds, from start to end.

        Note of Args `min_distance` and `duration`:
        - Both are using swipe (not flick) to adjust the element position.
        - `min_distance` and `duration` are interdependent.
        - The default settings are based on sliding at a rate of 100 pixels per second,
            which has been found to be stable.
        - It is advisable not to alter these unless specific conditions necessitate changes.

        Usage::

            # Default is flicking up.
            # offset = (0.5, 0.75, 0.5, 0.25) and area = (0.0, 0.0, 1.0, 1.0) means
            # x: Fixed 50% (0.5) of current window width (100% (1.0) window width).
            # y: From 75% (0.75) to 25% (0.25) of current window height (100% (1.0) window height).
            my_page.target_element.flick_by()

            # Flick with customize absolute offset.
            # Note that the area parameter will affect the adjusting process.
            # We recommend not setting the area in this case, 
            # unless you have a specific testing scenario.
            # (ex. flicking range is not within the area, 
            # and the target element should be inside the area after flicking.)
            my_page.target_element.flick_by((250, 300, 400, 700))

            # Flick with ratio of area.
            # Area is current window size (default).
            my_page.target_element.flick_by((0.3, 0.85, 0.5, 0.35))

            # Flick with ratio of area.
            # Area is ratio of current window size.
            my_page.target_element.flick_by((0.3, 0.85, 0.5, 0.35), (0.2, 0.2, 0.6, 0.8))

            # Flick with ratio of area.
            # Area is absolute coordinate.
            my_page.target_element.flick_by((0.3, 0.85, 0.5, 0.35), (100, 150, 300, 700))

            # Get absolute area coordinate by scrollable element rect.
            area = my_page.scrollable_element.rect
            my_page.target_element.flick_by((0.3, 0.85, 0.5, 0.35), area)

        """
        area = self.__get_area(area)
        offset = self.__get_offset(offset, area)
        self.__start_flicking_by(offset, timeout, max_flick)
        self.__start_adjusting_by(offset, area, max_adjust, min_distance, duration)
        return self

    def __get_coordinate(
        self,
        coordinate: Coordinate,
        name: str
    ) -> TupleCoordinate:

        # is dict or tuple
        if isinstance(coordinate, dict):
            values = tuple(coordinate.values())
        elif isinstance(coordinate, tuple):
            values = coordinate
        else:
            raise TypeError(f'"{name}" should be dict or tuple.')

        # is coordinate
        if all(isinstance(value, int) for value in values):
            values_type = int
        elif all(isinstance(value, float) for value in values):
            values_type = float
        else:
            raise TypeError(f'All "{name}" values should be "int" or "float".')

        # if float, all should be (0 <= x <= 1)
        if values_type == float and not all(0 <= value <= 1 for value in values):
            raise ValueError(f'All "{name}" values are floats and should be between "0.0" and "1.0".')

        return values

    def __get_area(self, area: Coordinate) -> tuple[int, int, int, int]:

        area_x, area_y, area_width, area_height = self.__get_coordinate(area, 'area')

        if isinstance(area_width, float):
            window_x, window_y, window_width, window_height = self._page.get_window_rect().values()
            area_x = window_x + int(window_width * area_x)
            area_y = window_y + int(window_height * area_y)
            area_width = int(window_width * area_width)
            area_height = int(window_height * area_height)

        area = (area_x, area_y, area_width, area_height)
        logstack._logging(f'🟢 area: {area}')
        return area

    def __get_offset(self,
        offset: Coordinate,
        area: tuple[int, int, int, int]
    ) -> tuple[int, int, int, int]:

        start_x, start_y, end_x, end_y = self.__get_coordinate(offset, 'offset')

        if isinstance(start_x, float):
            area_x, area_y, area_width, area_height = area
            start_x = area_x + int(area_width * start_x)
            start_y = area_y + int(area_height * start_y)
            end_x = area_x + int(area_width * end_x)
            end_y = area_y + int(area_height * end_y)

        offset = (start_x, start_y, end_x, end_y)
        logstack._logging(f'🟢 offset: {offset}')
        return offset

    def __start_swiping_by(
        self,
        offset: tuple[int, int, int, int],
        duration: int,
        timeout: int | float,
        max_swipe: int):
        logstack._logging(f'🟢 Start swiping to element {self.remark}.')
        count = 0
        while not self.is_viewable(timeout):
            if count == max_swipe:
                logstack._logging(
                    f'🟡 Stop swiping to element {self.remark} as the maximum swipe count of {max_swipe} has been reached.')
            self.driver.swipe(*offset, duration)
            count += 1
        logstack._logging(f'✅ End swiping as the element {self.remark} is now viewable.')
        return True

    def __start_flicking_by(
        self,
        offset: tuple[int, int, int, int],
        timeout: int | float,
        max_swipe: int):
        logstack._logging(f'🟢 Start flicking to element {self.remark}.')
        count = 0
        while not self.is_viewable(timeout):
            if count == max_swipe:
                logstack._logging(
                    f'🟡 Stop flicking to element {self.remark} as the maximum flick count of {max_swipe} has been reached.')
            self.driver.flick(*offset)
            count += 1
        logstack._logging(f'✅ End flicking as the element {self.remark} is now viewable.')
        return True

    def __start_adjusting_by(
        self,
        offset: tuple[int, int, int, int],
        area: tuple[int, int, int, int],
        max_adjust: int,
        min_distance: int,
        duration: int):
        def get_final_delta(delta):
            return int(math.copysign(min_distance, delta)) if abs(delta) < min_distance else delta

        logstack._logging(f'🟢 Start adjusting to element {self.remark}')

        for i in range(1, max_adjust + 2):

            # offset
            start_x, start_y, end_x, end_y = offset

            # area border
            area_left, area_top, area_width, area_height = area
            area_right = area_left + area_width
            area_bottom = area_top + area_height

            # element border
            element_left, element_right, element_top, element_bottom = self.border.values()

            # delta = (area - element) and compare with min distance
            delta_left = get_final_delta(area_left - element_left)
            delta_right = get_final_delta(area_right - element_right)
            delta_top = get_final_delta(area_top - element_top)
            delta_bottom = get_final_delta(area_bottom - element_bottom)

            # adjust condition
            adjust_left = delta_left > 0
            adjust_right = delta_right < 0
            adjust_top = delta_top > 0
            adjust_bottom = delta_bottom < 0
            adjust = (adjust_left, adjust_right, adjust_top, adjust_bottom)
            adjust_actions = {
                (True, False, True, False): (delta_left, delta_top),
                (False, False, True, False): (0, delta_top),
                (False, True, True, False): (delta_right, delta_top),
                (True, False, False, False): (delta_left, 0),
                (False, True, False, False): (delta_right, 0),
                (True, False, False, True): (delta_left, delta_bottom),
                (False, False, False, True): (0, delta_bottom),
                (False, True, False, True): (delta_right, delta_bottom),
            }

            # Set the end point by adjust actions.
            if adjust in adjust_actions:
                logstack._logging(f'🟢 Adjust (left, right, top, bottom): {adjust}')
                delta_x, delta_y = adjust_actions[adjust]
                end_x = start_x + delta_x
                end_y = start_y + delta_y
            else:
                logstack._logging(f'✅ End adjusting as the element {self.remark} is in area.')
                return True

            # max
            if i == max_adjust + 1:
                logstack._logging(
                    f'🟡 End adjusting to the element {self.remark} as the maximum adjust count of {max_adjust} has been reached.')
                return True

            self.driver.swipe(start_x, start_y, end_x, end_y, duration)

    def clear(self) -> WebElement | None:
        """
        Selenium and Appium API.
        Clear the text of the field type element.

        Returns:
        - None: Selenium.
        - WebElement: Appium.
        """
        try:
            return self._present_element.clear()
        except ElementException:
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
        element = self.present_element
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
        try:
            return self._present_element.get_attribute(name)
        except ElementException:
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
        try:
            return self._present_element.get_property(name)
        except ElementException:
            return self.wait_present(reraise=True).get_property(name)

    def submit(self) -> None:
        """
        Selenium API.
        Submits a form.
        """
        try:
            self._present_element.submit()
        except ElementException:
            self.wait_present(reraise=True).submit()

    @property
    def tag_name(self) -> str:
        """
        Selenium API.
        This element's `tagName` property.
        """
        try:
            return self._present_element.tag_name
        except ElementException:
            return self.wait_present(reraise=True).tag_name

    def value_of_css_property(self, property_name: Any) -> str:
        """
        Selenium API.
        The value of a CSS property.
        """
        try:
            return self._present_element.value_of_css_property(property_name)
        except ElementException:
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

    def action_click(self, perform: bool = True) -> Element:
        """
        Selenium ActionChains API.
        Clicks an element.

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.action_click()

            # Chain with another method
            my_page.my_element.scroll_to_element(False).action_click()
            
            # or
            my_page.my_element1.scroll_to_element(False).action_click(False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.click(self.present_element)
        if perform:
            action.perform()
        return self

    def click_and_hold(self, perform: bool = True) -> Element:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on an element.

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.click_and_hold()

            # Chain with another method
            my_page.my_element.scroll_to_element(False).click_and_hold()
            
            # or
            my_page.my_element1.scroll_to_element(False).click_and_hold(False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.click_and_hold(self.present_element)
        if perform:
            action.perform()
        return self

    def context_click(self, perform: bool = True) -> Element:
        """
        Selenium ActionChains API.
        Performs a context-click (right click) on an element.

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.context_click()

            # Chain with another method
            my_page.my_element.scroll_to_element(False).context_click()
            
            # or
            my_page.my_element1.scroll_to_element(False).context_click(False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.context_click(self.present_element)
        if perform:
            action.perform()
        return self

    def double_click(self, perform: bool = True) -> Element:
        """
        Selenium ActionChains API.
        Double-clicks an element.

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.double_click()

            # Chain with another method
            my_page.my_element.scroll_to_element(False).double_click()
            
            # or
            my_page.my_element1.scroll_to_element(False).double_click(False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.double_click(self.present_element)
        if perform:
            action.perform()
        return self

    def drag_and_drop(
        self,
        target: Element | SeleniumWebElement,
        perform: bool = True
    ) -> Element:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on the source element, 
        then moves to the target element and releases the mouse button.

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element1.drag_and_drop(my_page.my_element2)

            # Chain with another method
            my_page.my_element1.scroll_to_element(False).drag_and_drop(my_page.my_element2)
            
            # or
            my_page.my_element1.scroll_to_element(False).drag_and_drop(my_page.my_element2, False)
            ...  # other process
            my_page.perform()
        """
        source = self.present_element
        if isinstance(target, Element):
            target = target.present_element
        action = self._action.drag_and_drop(source, target)
        if perform:
            action.perform()
        return self

    def drag_and_drop_by_offset(
        self,
        xoffset: int,
        yoffset: int,
        perform: bool = True
    ) -> Element:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on the source element,
        then moves to the target offset and releases the mouse button.

        Args:
        - xoffset: X offset to move to, as a positive or negative integer.
        - yoffset: Y offset to move to, as a positive or negative integer.
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.drag_and_drop_by_offset(100, 200)

            # Chain with another method
            my_page.my_element.scroll_to_element(False).drag_and_drop_by_offset(100, 200)
            
            # or
            my_page.my_element.scroll_to_element(False).drag_and_drop_by_offset(100, 200, False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.drag_and_drop_by_offset(self.present_element, xoffset, yoffset)
        if perform:
            action.perform()
        return self

    def move_to_element(self, perform: bool = True) -> Element:
        """
        Selenium ActionChains API.
        Moving the mouse to the middle of an element.

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.move_to_element()

            # Chain with another method
            my_page.my_element.scroll_to_element(False).move_to_element()
            
            # or
            my_page.my_element.scroll_to_element(False).move_to_element(False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.move_to_element(self.present_element)
        if perform:
            action.perform()
        return self

    def move_to_element_with_offset(
        self,
        xoffset: int,
        yoffset: int,
        perform: bool = True
    ) -> Element:
        """
        Selenium ActionChains API.
        Move the mouse by an offset of the specified element.
        Offsets are relative to the in-view center point of the element.

        Args:
        - xoffset: X offset to move to, as a positive or negative integer.
        - yoffset: Y offset to move to, as a positive or negative integer.
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.move_to_element_with_offset(100, 200)

            # Chain with another method
            my_page.my_element.scroll_to_element(False).move_to_element_with_offset(100, 200)
            
            # or
            my_page.my_element.scroll_to_element(False).move_to_element_with_offset(100, 200, False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.move_to_element_with_offset(self.present_element, xoffset, yoffset)
        if perform:
            action.perform()
        return self

    def release(self, perform: bool = True) -> Element:
        """
        Selenium ActionChains API.
        Releasing a held mouse button on an element.

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.release()

            # Chain with another method
            my_page.my_element.click_and_hold(False).release()
            
            # or
            my_page.my_element.click_and_hold(False).release(False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.release(self.present_element)
        if perform:
            action.perform()
        return self

    def send_keys_to_element(self, perform: bool = True, *keys_to_send: str) -> Element:
        """
        Selenium ActionChains API.
        Sends keys to an element

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.
        - keys_to_send: The keys to send. Modifier keys constants can be found in the 'Keys' class.

        Usage::

            # Basic usage
            my_page.my_element.send_keys_to_element(True, Keys.ENTER)

            # Chain with another method
            my_page.my_element.scroll_to_element(False).send_keys_to_element(True, Keys.ENTER)
            
            # or
            my_page.my_element.scroll_to_element(False).send_keys_to_element(False, Keys.ENTER)
            ...  # other process
            my_page.perform()
        """
        # TODO Need to check the perform position.
        action = self._action.send_keys_to_element(self.present_element, *keys_to_send)
        if perform:
            action.perform()
        return self

    def scroll_to_element(self, perform: bool = True) -> Element:
        """
        Selenium API.
        If the element is outside the viewport,
        scrolls the bottom of the element to the bottom of the viewport.

        Args:
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.scroll_to_element()

            # Chain with another method
            my_page.my_element.scroll_to_element(False).action_click()
            
            # or
            my_page.my_element1.scroll_to_element(False).action_click(False)
            ...  # other process
            my_page.perform()
        """
        action = self._action.scroll_to_element(self.present_element)
        if perform:
            action.perform()
        return self

    def scroll_from_element(
            self, 
            x_offset: int = 0, 
            y_offset: int = 0,
            delta_x: int = 0, 
            delta_y: int = 0,
            perform: bool = True
    ):
        """
        Selenium ActionChains API.
        Set the origin to the center of the element with an offset,
        and perform the swipe with the specified delta.
        If the element is not in the viewport, 
        the bottom of the element will first be scrolled to the bottom of the viewport.

        Args:
        - x_offset: from origin element center, a negative value offset left.
        - y_offset: from origin element center, a negative value offset up.
        - delta_x: Distance along X axis to scroll using the wheel. A negative value scrolls left.
        - delta_y: Distance along Y axis to scroll using the wheel. A negative value scrolls up.
        - perform: Default is True to perform the stored action immediately; 
            otherwise, store the action to be performed later.

        Usage::

            # Basic usage
            my_page.my_element.scroll_from_element(100, 200, -50, -100)

            # Chain with another method
            my_page.my_element.scroll_to_element(False).action_click()
            
            # or
            my_page.my_element1.scroll_to_element(False).action_click(False)
            ...  # other process
            my_page.perform()
        """
        scroll_origin = ScrollOrigin.from_element(self.present_element, x_offset, y_offset)
        action = self._action.scroll_from_origin(scroll_origin, delta_x, delta_y)
        if perform:
            action.perform()
        return self
    
    # TODO select reuse method
    @property
    def _select(self):
        self.__select = Select(self.present_element)
        return self.__select
    
    @property
    def select(self):
        try:
            result = self.__select
            logstack.info('✅ self.__select')
        except ElementException:
            result = self._select
            logstack.info('✅ self._select')
        return result
    
    @property
    def options(self) -> list[SeleniumWebElement]:
        """
        Selenium Select API.
        Returns a list of all options belonging to this select tag.
        """
        self.select.options

    @property
    def all_selected_options(self) -> list[SeleniumWebElement]:
        """
        Selenium Select API.
        Returns a list of all selected options belonging to this select tag.
        """
        self.select.all_selected_options

    @property
    def first_selected_option(self) -> SeleniumWebElement:
        """
        Selenium Select API.
        The first selected option in this select tag (or the currently selected option in a normal select)
        """
        self.select.first_selected_option

    def select_by_value(self, value: str) -> None:
        """
        Selenium Select API.
        Select all options that have a value matching the argument.

        That is, when given "foo" this would select an option like:
        <option value="foo">Bar</option>

        Args:
        - value: The value to match against
        """
        self.select.select_by_value(value)

    def select_by_index(self, index: int) -> None:
        """
        Selenium API.
        Select the option at the given index.

        This is done by examining the "index" attribute of an element, and not merely by counting.

        :Args:
        index - The option at this index will be selected
        throws NoSuchElementException If there is no option with specified index in SELECT
        """
        self.select.select_by_index(index)

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
        self.select.select_by_visible_text(text)

    def deselect_all(self) -> None:
        """
        Selenium Select API.
        Clear all selected entries.
        This is only valid when the SELECT supports multiple selections.
        """
        self.select.deselect_all()

    def deselect_by_value(self, value: str) -> None:
        """
        Selenium Select API.
        Deselect all options that have a value matching the argument. That is, when given "foo" this would deselect an option like:
        <option value="foo">Bar</option>

        Args:
        - value: The value to match against
        """
        self.select.deselect_by_value(value)

    def deselect_by_index(self, index: int) -> None:
        """
        Selenium Select API.
        Deselect the option at the given index. 
        This is done by examining the "index" attribute of an element, 
        and not merely by counting.

        Args:
        - index: The option at this index will be deselected
        """
        self.select.deselect_by_index(index)

    def deselect_by_visible_text(self, text: str) -> None:
        """
        Selenium Select API.
        Deselect all options that display text matching the argument. 
        That is, when given "Bar" this would deselect an option like:
        <option value="foo">Bar</option>

        Args:
        - text: The visible text to match against
        """
        self.select.deselect_by_visible_text(text)

    @property
    def location_in_view(self) -> dict[str, int]:
        """
        Appium API.
        Retrieve the location (coordination) of the element relative to the view when it is present.
        Return: {'x': int, 'y': int}
        """
        try:
            return self._present_element.location_in_view
        except ElementException:
            return self.wait_present(reraise=True).location_in_view

    def enter(self) -> None:
        """
        Selenium API
        Send keys ENTER to the element.
        """
        try:
            self._present_element.send_keys(Keys.ENTER)
        except ElementException:
            self.wait_present(reraise=True).send_keys(Keys.ENTER)

    def select_all(self) -> None:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + A" to the element.
        """
        first = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        try:
            self._present_element.send_keys(first, 'a')
        except ElementException:
            self.wait_present(reraise=True).send_keys(first, 'a')

    def cut(self) -> None:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + X" to the element.
        """
        first = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        try:
            self._present_element.send_keys(first, 'x')
        except ElementException:
            self.wait_present(reraise=True).send_keys(first, 'x')

    def copy(self) -> None:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + C" to the element.
        """
        first = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        try:
            self._present_element.send_keys(first, 'c')
        except ElementException:
            self.wait_present(reraise=True).send_keys(first, 'c')

    def paste(self) -> None:
        """
        Selenium API
        Send keys "COMMAND/CONTROL + V" to the element.
        """
        first = Keys.COMMAND if platform.system().lower() == "darwin" else Keys.CONTROL
        try:
            self._present_element.send_keys(first, 'v')
        except ElementException:
            self.wait_present(reraise=True).send_keys(first, 'v')

    def backspace(self) -> None:
        """
        Selenium API
        Send keys BACKSPACE to the element.
        """
        try:
            self._present_element.send_keys(Keys.BACKSPACE)
        except ElementException:
            self.wait_present(reraise=True).send_keys(Keys.BACKSPACE)

    def delete(self) -> None:
        """
        Selenium API
        Send keys DELETE to the element.
        """
        try:
            self._present_element.send_keys(Keys.DELETE)
        except ElementException:
            self.wait_present(reraise=True).send_keys(Keys.DELETE)

    def tab(self) -> None:
        """
        Selenium API
        Send keys TAB to the element.
        """
        try:
            self._present_element.send_keys(Keys.TAB)
        except ElementException:
            self.wait_present(reraise=True).send_keys(Keys.TAB)

    def space(self) -> None:
        """
        Selenium API
        Send keys SPACE to the element.
        """
        try:
            self._present_element.send_keys(Keys.SPACE)
        except ElementException:
            self.wait_present(reraise=True).send_keys(Keys.SPACE)

    def swipe_into_view(
        self,
        direction: str = SA.V,
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
        # TODO deprecate
        warnings.warn(
            'This function is deprecated and will be removed in future versions. Please use "swipe_by" instead.',
            DeprecationWarning,
            stacklevel=2)

        # Get border.
        border = self.__get_border(direction, border)

        # Determine v or h, and actual swiping range.
        coordinate = self.__get_range(direction, *border, start, end, fix)

        # Start swiping and check whether it is viewable in max count of swiping.
        self.__start_swiping(*coordinate, duration, timeout, max_swipe)

        # Start adjusting when element is viewable.
        self.__start_adjusting(*border, *coordinate, max_adjust, min_distance, duration)

        # Return self to re-trigger the element finding process, thereby avoiding staleness issues.
        return self

    def __get_border(
        self,
        direction: str,
        border: dict[str, int] | tuple[int, int, int, int]):
        """
        Usage::

            return left, right, top, bottom
        """
        # Get border.
        if isinstance(border, dict):
            left, right, top, bottom = border.values()
        elif isinstance(border, tuple):
            left, right, top, bottom = border
        else:
            raise TypeError('Parameter "border" should be dict or tuple.')

        if 'a' not in direction.lower():
            window_left, window_top, window_width, window_height = self._page.get_window_rect().values()
            left, right = [int(window_left + window_width * x / 100) for x in (left, right)]
            top, bottom = [int(window_top + window_height * y / 100) for y in (top, bottom)]

        border = (left, right, top, bottom)
        logstack._logging(f'✅ border: {border}')
        return border

    def __get_range(
        self,
        direction: str,
        left: int,
        right: int,
        top: int,
        bottom: int,
        start: int,
        end: int,
        fix: bool | int = False):
        """
        Usage::

            return sx, sy, ex, ey
        """
        width = right - left
        height = bottom - top

        # Determine v or h, and actual swiping range.
        if 'v' in direction.lower():
            sy = top + int(height * start / 100)
            ey = top + int(height * end / 100)
            if fix is False:
                # border center x
                sx = ex = left + int(width / 2)
            elif fix is True:
                # element center x
                sx = ex = self.center['x']
            elif isinstance(fix, int):
                # absolute x
                sx = ex = fix
            else:
                raise TypeError('Parameter "fix" should be bool or int.')
        elif 'h' in direction.lower():
            sx = left + int(width * start / 100)
            ex = left + int(width * end / 100)
            if fix is False:
                # border center y
                sy = ey = top + int(height / 2)
            elif fix is True:
                # element center y
                sy = ey = self.center['y']
            elif isinstance(fix, int):
                # absolute y
                sy = ey = fix
            else:
                raise TypeError('Parameter "fix" should be bool or int.')
        else:
            raise ValueError(f'Parameter "dirtype" should be {SA.V}, {SA.VA}, {SA.H} or {SA.HA}.')

        coordinate = (sx, sy, ex, ey)
        logstack._logging(f'✅ coordinate: {coordinate}')
        return coordinate

    def __start_swiping(
        self,
        sx: int,
        sy: int,
        ex: int,
        ey: int,
        duration: int,
        timeout: int | float,
        max_swipe: int):
        """
        Return viewable or not.
        """
        logstack._logging(f'🟢 Start swiping to element {self.remark}.')
        count = 0
        while not self.is_viewable(timeout):
            if count == max_swipe:
                raise ValueError(
                    f'Stop swiping to element {self.remark} as the maximum swipe count of {max_swipe} has been reached.')
            self.driver.swipe(sx, sy, ex, ey, duration)
            count += 1
        logstack._logging(f'✅ End swiping as the element {self.remark} is now viewable.')
        return True

    def __start_adjusting(
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
        duration: int):
        """
        Start adjusting.
        """
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
                logstack._logging(
                    f'🟡 End adjusting to the element {self.remark} as the maximum adjust count of {max_adjust} has been reached.')
                return True
            self.driver.swipe(sx, sy, ex, ey, duration)