# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# TODO selenium 4.0 and appium 2.0 methods.
# TODO Need to confirm the functional difference between 'driver' and 'page'.
# TODO Tracking the range using wait function.

from __future__ import annotations

import warnings
from typing import Any, Literal, TypeAlias

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.print_page_options import PrintOptions

from . import logstack
from . import ec_extension as ecex
from .config import Timeout
from .types import AppiumWebDriver
from .types import WebDriver, WebElement, WebDriverTuple

# TODO deprecate
from .by import SwipeAction as SA

IntCoordinate: TypeAlias = dict[str, int] | tuple[int, int, int, int]
FloatCoordinate: TypeAlias = dict[str, float] | tuple[float, float, float, float]
TupleCoordinate: TypeAlias = tuple[int, int, int, int] | tuple[float, float, float, float]
Coordinate: TypeAlias = IntCoordinate | FloatCoordinate


class Page:

    def __init__(self, driver: WebDriver) -> None:
        if not isinstance(driver, WebDriverTuple):
            raise TypeError(f'The driver type should be "WebDriver", not {type(driver).__name__}.')
        self._driver = driver
        self._action = ActionChains(driver)

    @property
    def driver(self) -> WebDriver:
        return self._driver

    @property
    def action(self) -> ActionChains:
        """
        Calling instance of ActionChains.
        You can use it to perform an ActionChains method.

        Usage::

            my_page.action.scroll_to_element(element).click(element)
        """
        return self._action

    def wait(self, timeout: int | float | None = None) -> WebDriverWait:
        """
        Selenium and Appium API.
        Packing WebDriverWait(driver, timeout) to accept only the timeout parameter.

        Args:
        - timeout: Maximum time in seconds to wait for the expected condition.
        """
        self._wait_timeout = Timeout.DEFAULT if timeout is None else timeout
        return WebDriverWait(self.driver, self._wait_timeout)

    @property
    def wait_timeout(self) -> int | float | None:
        """
        Get the final waiting timeout of the page function 
        which executed with explicit wait.
        If no relevant function has been executed yet,
        it will return None.
        """
        try:
            return self._wait_timeout
        except AttributeError:
            return None

    def get(self, url: str) -> None:
        """
        Loads a web page in the current browser session.
        """
        self.driver.get(url)

    @property
    def source(self) -> str:
        """
        Gets the source of the current page.
        It is the same as driver.page_source.
        """
        return self.driver.page_source

    @property
    def url(self) -> str:
        """
        Selenium API.
        Gets the URL of the current page.
        It is the same as driver.current_url.
        """
        return self.driver.current_url

    def url_is(
        self,
        url: str,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Selenium API.
        An expectation for checking the current url,
        url is the expected url,
        which must be an exact match returns True if the url matches, False otherwise.
        """
        try:
            # We don't set the TimeoutException message in the until method
            # because we want to catch the behavior that occurs after a timeout.
            return self.wait(timeout).until(ec.url_to_be(url))
        except TimeoutException:
            if Timeout.reraise(reraise):
                current_url = self.driver.current_url  # Get url after timeout.
                message = (f'Wait for url to be {url} timed out after {timeout} seconds. '
                           f'The current url is {current_url}')
                raise TimeoutException(message) from None
            return False

    def url_contains(
        self,
        url: str,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Selenium API.
        An expectation for checking that the current url contains a case-sensitive substring,
        url is the fragment of url expected,
        returns True when the url matches, False otherwise.
        """
        try:
            # We don't set the TimeoutException message in the until method
            # because we want to catch the behavior that occurs after a timeout.
            return self.wait(timeout).until(ec.url_contains(url))
        except TimeoutException:
            if Timeout.reraise(reraise):
                current_url = self.driver.current_url  # Get url after timeout.
                message = (f'Wait for url contains {url} timed out after {timeout} seconds. '
                           f'The current url is {current_url}')
                raise TimeoutException(message) from None
            return False

    def url_matches(
        self,
        pattern: str,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Selenium API.
        An expectation for checking the current url,
        pattern is the expected pattern.
        This finds the first occurrence of pattern in the current url
        and as such does not require an exact full match.
        """
        try:
            # We don't set the TimeoutException message in the until method
            # because we want to catch the behavior that occurs after a timeout.
            return self.wait(timeout).until(ec.url_matches(pattern))
        except TimeoutException:
            if Timeout.reraise(reraise):
                current_url = self.driver.current_url  # Get url after timeout.
                message = (f'Wait for url matches {pattern} timed out after {timeout} seconds. '
                           f'The current url is {current_url}')
                raise TimeoutException(message) from None
            return False

    def url_changes(
        self,
        url: str,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Selenium API.
        An expectation for checking the current url,
        url is the expected url,
        which must not be an exact match returns True if the url is different, false otherwise.
        """
        try:
            # We don't set the TimeoutException message in the until method
            # because we want to catch the behavior that occurs after a timeout.
            return self.wait(timeout).until(ec.url_changes(url))
        except TimeoutException:
            if Timeout.reraise(reraise):
                current_url = self.driver.current_url  # Get url after timeout.
                message = (f'Wait for url changes to {url} timed out after {timeout} seconds. '
                           f'The current url is {current_url}')
                raise TimeoutException(message) from None
            return False

    @property
    def title(self):
        """
        Selenium API.
        Returns the title of the current page.
        """
        return self.driver.title

    def title_is(
        self,
        title: str,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Selenium API.
        An expectation for checking the title of a page.
        title is the expected title,
        which must be an exact match returns True if the title matches, false otherwise.
        """
        try:
            # We don't set the TimeoutException message in the until method
            # because we want to catch the behavior that occurs after a timeout.
            return self.wait(timeout).until(ec.title_is(title))
        except TimeoutException:
            if Timeout.reraise(reraise):
                current_title = self.driver.title  # Get title after timeout.
                message = (f'Wait for title to be {title} timed out after {timeout} seconds. '
                           f'The current title is {current_title}')
                raise TimeoutException(message) from None
            return False

    def title_contains(
        self,
        title: str,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        Selenium API.
        An expectation for checking that the title contains a case-sensitive substring.
        title is the fragment of title expected returns True when the title matches, False otherwise
        """
        try:
            # We don't set the TimeoutException message in the until method
            # because we want to catch the behavior that occurs after a timeout.
            return self.wait(timeout).until(ec.title_contains(title))
        except TimeoutException:
            if Timeout.reraise(reraise):
                current_title = self.driver.title  # Get title after timeout.
                message = (f'Wait for title contains {title} timed out after {timeout} seconds. '
                           f'The current title is {current_title}')
                raise TimeoutException(message) from None
            return False

    def refresh(self) -> None:
        """
        Selenium API.
        Refreshes the current page.
        """
        self.driver.refresh()

    def back(self) -> None:
        """
        Selenium API.
        Goes one step backward in the browser history.
        """
        self.driver.back()

    def forward(self) -> None:
        """
        Selenium API.
        Goes one step forward in the browser history.
        """
        self.driver.forward()

    def close(self) -> None:
        """
        Selenium API, driver method.
        Closes the current window.
        """
        self.driver.close()

    def quit(self) -> None:
        """
        Driver method.
        Quits the driver and closes every associated window.
        """
        self.driver.quit()

    @property
    def current_window_handle(self) -> str:
        """
        Returns the handle of the current window.
        """
        return self.driver.current_window_handle

    @property
    def window_handles(self) -> list[str]:
        """
        Returns the handles of all windows within the current session.
        """
        return self.driver.window_handles

    def maximize_window(self) -> None:
        """
        Maximizes the current window that webdriver is using.
        """
        self.driver.maximize_window()

    def fullscreen_window(self) -> None:
        """
        Invokes the window manager-specific 'full screen' operation.
        """
        self.driver.fullscreen_window()

    def minimize_window(self) -> None:
        """
        Invokes the window manager-specific 'minimize' operation.
        """
        self.driver.minimize_window()

    def set_window_rect(
        self,
        x: int | None = None,
        y: int | None = None,
        width: int | None = None,
        height: int | None = None
    ) -> dict | None:
        """
        Sets the x, y coordinates of the window as well as height and width of the current window.
        This method is only supported for W3C compatible browsers;
        other browsers should use set_window_position and set_window_size.

        Usage::

            page.set_window_rect(x=10, y=10)
            page.set_window_rect(width=100, height=200)
            page.set_window_rect(x=10, y=10, width=100, height=200)

        """
        if x is None and y is None and width is None and height is None:
            self.driver.maximize_window()
        else:
            return self.driver.set_window_rect(x, y, width, height)

    def get_window_rect(self) -> dict:
        """
        Gets the x, y coordinates of the window as well as height and width of the current window.

        Return is rearranged, for example: 
        {'x': 0, 'y': 0, 'width': 500, 'height': 250}

        Note that the value type is the same as official.
        """
        rect = self.driver.get_window_rect()
        return {'x': rect['x'], 'y': rect['y'], 'width': rect['width'], 'height': rect['height']}

    def set_window_position(
        self,
        x: int = 0,
        y: int = 0,
        windowHandle: str = 'current'
    ) -> dict:
        """
        Sets the x,y position of the current window. (window.moveTo)

        Args:
            - x: the x-coordinate in pixels to set the window position
            - y: the y-coordinate in pixels to set the window position

        Usage::

            page.set_window_position(0,0)

        """
        return self.driver.set_window_position(x, y, windowHandle)

    def get_window_position(self, windowHandle: str = "current") -> dict:
        """
        Gets the x, y coordinates of the window as well as height and width of the current window.

        Return: {'x': 0, 'y': 0}
        """
        return self.driver.get_window_position(windowHandle)

    def set_window_size(
        self,
        width: int | None = None,
        height: int | None = None,
        windowHandle: str = 'current'
    ) -> None:
        """
        selenium API
        Sets the width and height of the current window.

        Args:
        - width: the width in pixels to set the window to
        - height: the height in pixels to set the window to
        """
        if width is None and height is None:
            self.driver.maximize_window()
        else:
            self.driver.set_window_size(width, height, windowHandle)

    def get_window_size(self, windowHandle: str = 'current') -> dict:
        """
        Gets the width and height of the current window.

        Return: {'width': 430, 'height': 920}
        """
        return self.driver.get_window_size(windowHandle)

    def get_window_border(self) -> dict[str, int]:
        """
        window border: {'left': int, 'right': int, 'top': int, 'bottom': int}
        """
        rect = self.driver.get_window_rect()
        left = int(rect['x'])
        right = int(rect['x'] + rect['width'])
        top = int(rect['y'])
        bottom = int(rect['y'] + rect['height'])
        return {'left': left, 'right': right, 'top': top, 'bottom': bottom}

    def get_window_center(self) -> dict[str, int]:
        """
        window center: {'x': int, 'y': int}
        """
        rect = self.driver.get_window_rect()
        x = int(rect['x'] + rect['width'] / 2)
        y = int(rect['y'] + rect['height'] / 2)
        return {'x': x, 'y': y}

    def number_of_windows_to_be(
        self,
        num_windows: int,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        An expectation for the number of windows to be a certain value.
        """
        try:
            return self.wait(timeout).until(ec.number_of_windows_to_be(num_windows))
        except TimeoutException:
            if Timeout.reraise(reraise):
                current_num_windows = len(self.driver.window_handles)
                message = (f'Wait for number of windows to be {num_windows} timed out after {timeout} seconds. '
                           f'The current number of windows is {current_num_windows}')
                raise TimeoutException(message) from None
            return False

    def new_window_is_opened(
        self,
        current_handles: list[str],
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> bool:
        """
        An expectation for the number of windows to be a certain value.
        """
        try:
            return self.wait(timeout).until(ec.new_window_is_opened(current_handles))
        except TimeoutException:
            if Timeout.reraise(reraise):
                current_num_windows = len(self.driver.window_handles)
                message = (f'Wait for new window is opened timed out after {timeout} seconds. '
                           f'The current number of windows is {current_num_windows}')
                raise TimeoutException(message) from None
            return False

    def print_pdf(self, print_options: PrintOptions | None = None) -> str:
        """
        Takes PDF of the current page.
        The driver makes a best effort to return a PDF based on the provided parameters.
        """
        return self.driver.print_page(print_options)

    def execute_script(self, script, *args) -> Any:
        """
        Synchronously Executes JavaScript in the current window or frame.

        Args:
        - script: The JavaScript to execute.
        - *args: Any applicable arguments for your JavaScript.

        Usage::

            driver.execute_script('return document.title;')

        """
        return self.driver.execute_script(script, *args)

    def execute_async_script(self, script: str, *args) -> Any:
        """
        Asynchronously Executes JavaScript in the current window/frame.

        Args:
        - script: The JavaScript to execute.
        - *args: Any applicable arguments for your JavaScript.

        Usage::

            script = "var callback = arguments[arguments.length - 1]; " \\
                     "window.setTimeout(function(){ callback('timeout') }, 3000);"
            driver.execute_async_script(script)

        """
        return self.driver.execute_async_script(script, *args)

    def perform(self) -> None:
        """
        Selenium ActionChains API.
        Performs all stored actions.
        once called, it will execute all stored actions in page.

        Usage::

            # Perform all saved actions:
            my_page.my_element1.scroll_to_element().action_click()
            my_page.my_element2.drag_and_drop(my_page.element3)
            my_page.perform()
        """
        self._action.perform()

    def reset_actions(self) -> None:
        """
        Selenium ActionChains API.
        Clears actions that are already stored in object of Page.
        once called, it will reset all stored actions in page.

        Usage::

            # Reset all saved actions:
            my_page.my_element1.scroll_to_element().action_click()
            my_page.my_element2.drag_and_drop(my_page.element3)
            my_page.reset_actions()
        """
        self._action.reset_actions()

    def click(self) -> Page:
        """
        Selenium ActionChains API.
        clicks on current mouse position.
        """
        self._action.click()
        return self

    def click_and_hold(self) -> Page:
        """
        Selenium ActionChains API.
        Holds down the left mouse button on current mouse position.
        """
        self._action.click_and_hold()
        return self

    def context_click(self) -> Page:
        """
        Selenium ActionChains API.
        Performs a context-click (right click) on current mouse position.
        """
        self._action.context_click()
        return self

    def double_click(self) -> Page:
        """
        Selenium ActionChains API.
        Double-clicks on current mouse position.
        """
        self._action.double_click()
        return self

    def key_down(self, value: str) -> Page:
        """
        Selenium ActionChains API.
        Sends a key press only to a focused element, without releasing it. 
        Should only be used with modifier keys (Control, Alt and Shift).

        Args:
        - value: The modifier key to send. Values are defined in Keys class.
        """
        self._action.key_down(value)
        return self

    def key_up(self, value: str) -> Page:
        """
        Selenium ActionChains API.
        Releases a modifier key on a focused element.

        Args:
        - value: The modifier key to send. Values are defined in Keys class.
        """
        self._action.key_up(value)
        return self

    def move_by_offset(self, xoffset: int, yoffset: int) -> Page:
        """
        Selenium ActionChains API.
        Moving the mouse to an offset from current mouse position.

        Args:
        - xoffset: X offset to move to, as a positive or negative integer.
        - yoffset: Y offset to move to, as a positive or negative integer.
        """
        self._action.move_by_offset(xoffset, yoffset)
        return self

    def pause(self, seconds: int | float) -> Page:
        """
        Selenium ActionChains API.
        Pause all inputs for the specified duration in seconds.
        """
        self._action.pause(seconds)
        return self

    def release(self) -> Page:
        """
        Selenium ActionChains API.
        Releasing a held mouse button on current mouse position.
        """
        self._action.release()
        return self

    def send_keys(self, *keys_to_send: str) -> Page:
        """
        Selenium ActionChains API.
        Sends keys to current focused element.
        """
        self._action.send_keys(*keys_to_send)
        return self

    def scroll_by_amount(self, delta_x: int, delta_y: int) -> Page:
        """
        Selenium ActionChains API.
        Scrolls by provided amounts with the origin in the top left corner of the viewport.

        Args:
        - delta_x: Distance along X axis to scroll using the wheel. A negative value scrolls left.
        - delta_y: Distance along Y axis to scroll using the wheel. A negative value scrolls up.
        """
        self.action.scroll_by_amount(delta_x, delta_y)
        return self

    def scroll_from_origin(
        self,
        x_offset: int = 0,
        y_offset: int = 0,
        delta_x: int = 0,
        delta_y: int = 0,
    ) -> Page:
        """
        Selenium ActionChains API.
        Scrolls by provided amount based on a provided origin. 
        The scroll origin is the upper left of the viewport plus any offsets. 

        Args:
        - x_offset: from origin viewport, a negative value offset left.
        - y_offset: from origin viewport, a negative value offset up.
        - delta_x: Distance along X axis to scroll using the wheel. A negative value scrolls left.
        - delta_y: Distance along Y axis to scroll using the wheel. A negative value scrolls up.

        Raises: If the origin with offset is outside the viewport.
        - MoveTargetOutOfBoundsException - If the origin with offset is outside the viewport.
        """
        scroll_origin = ScrollOrigin.from_viewport(x_offset, y_offset)
        self._action.scroll_from_origin(scroll_origin, delta_x, delta_y)
        return self

    def tap(
        self,
        positions: list[tuple[int, int]],
        duration: int | None = None
    ) -> AppiumWebDriver:
        """
        Appium API.
        Taps on an particular place with up to five fingers, holding for a certain time

        Args:
            positions: an array of tuples representing the x/y coordinates of
                the fingers to tap. Length can be up to five.
            duration: length of time to tap, in ms. Default value is 100 ms.

        Usage::

            page.tap([(100, 20), (100, 60), (100, 100)], 500)
        """
        return self.driver.tap(positions, duration)

    def tap_window_center(self, duration: int | None = None) -> AppiumWebDriver:
        """
        Tap window center coordination.

        Args:
        - duration: length of time to tap, in ms. Default value is 100 ms.
        """
        window_center = [tuple(self.get_window_center().values())]
        return self.driver.tap(window_center, duration)

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 0) -> AppiumWebDriver:
        """
        Swipe from one point to another point, for an optional duration.

        Args:
        - start_x: x-coordinate at which to start
        - start_y: y-coordinate at which to start
        - end_x: x-coordinate at which to stop
        - end_y: y-coordinate at which to stop
        - duration: defines the swipe speed as time taken to swipe from point a to point b, in ms,
          note that default set to 250 by ActionBuilder.

        Usage::

            page.swipe(100, 100, 100, 400)

        """
        return self.driver.swipe(start_x, start_y, end_x, end_y, duration)

    def swipe_by(
        self,
        offset: Coordinate = {'start_x': 0.5, 'start_y': 0.75, 'end_x': 0.5, 'end_y': 0.25},
        area: Coordinate = {'x': 0.0, 'y': 0.0, 'width': 1.0, 'height': 1.0},
        duration: int = 1000,
        times: int = 1
    ) -> AppiumWebDriver:
        """
        Swipe from one point to another, allowing customization of the offset and border settings.

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
        - duration: Defines the swipe speed as the time taken to swipe from point A to point B, in milliseconds. 
            The default is set to 250 by ActionBuilder.
        - times: The number of times to perform the swipe.

        Usage::

            # Default is swiping down.
            # x: Fixed 50% (half) of current window width.
            # y: From 75% to 25% of current window height.
            my_page.swipe_by()

            # Swipe with customize absolute offset.
            # Note that the area parameter will not affect any swiping behavior.
            my_page.swipe_by((250, 300, 400, 700))

            # Swipe with ratio of border.
            # Area is current window size (default).
            my_page.swipe_by((0.3, 0.85, 0.5, 0.35))

            # Swipe with ratio of border.
            # Area is ratio of current window size.
            my_page.swipe_by((0.3, 0.85, 0.5, 0.35), (0.2, 0.2, 0.6, 0.8))

            # Swipe with ratio of border.
            # Area is absolute coordinate.
            my_page.swipe_by((0.3, 0.85, 0.5, 0.35), (100, 150, 300, 700))

            # Get absolute border coordinate by scrollable element rect.
            area = my_page.scrollable_element.rect
            my_page.swipe_by((0.3, 0.85, 0.5, 0.35), area)
        """

        area = self.__get_area(area)
        offset = self.__get_offset(offset, area)

        for _ in range(times):
            driver = self.driver.swipe(*offset, duration)

        return driver

    def flick(self, start_x: int, start_y: int, end_x: int, end_y: int) -> AppiumWebDriver:
        """
        Appium API.
        Flick from one point to another point.

        Args:
            start_x: x-coordinate at which to start
            start_y: y-coordinate at which to start
            end_x: x-coordinate at which to stop
            end_y: y-coordinate at which to stop

        Usage:
            page.flick(100, 100, 100, 400)
        """
        return self.driver.flick(start_x, start_y, end_x, end_y)

    def flick_by(
        self,
        offset: Coordinate = {'start_x': 0.5, 'start_y': 0.75, 'end_x': 0.5, 'end_y': 0.25},
        area: Coordinate = {'x': 0.0, 'y': 0.0, 'width': 1.0, 'height': 1.0},
        times: int = 1
    ) -> AppiumWebDriver:
        """
        Flick from one point to another, allowing customization of the offset and border settings.

        Args:
        - offset: The flicking range, which can be set as:
            - int: The absolute coordinates.
                - dict: {'start_x': int, 'start_y': int, 'end_x': int, 'end_y': int}
                - tuple: (int, int, int, int) corresponding to the keys in the dict.
            - float: The ratio of the border (flickable range), which should be between 0.0 and 1.0.
                - dict: {'start_x': float, 'start_y': float, 'end_x': float, 'end_y': float}
                - tuple: (float, float, float, float) corresponding to the keys in the dict.
        - area: The flickable area, default is the current window size, which can be set as:
            - int: The absolute rectangle.
                - dict: {'x': int, 'y': int, 'width': int, 'height': int}
                - tuple: (int, int, int, int) corresponding to the keys in the dict.
            - float: The ratio of the current window size, which should be between 0.0 and 1.0.
                - dict: {'x': float, 'y': float, 'width': float, 'height': float}
                - tuple: (float, float, float, float) corresponding to the keys in the dict.
        - times: The number of times to perform the flick.

        Usage::

            # Default is flicking down.
            # x: Fixed 50% (half) of current window width.
            # y: From 75% to 25% of current window height.
            my_page.flick_by()

            # Flick with customize absolute offset.
            # Note that the area parameter will not affect any swiping behavior.
            my_page.flick_by((250, 300, 400, 700))

            # Flick with ratio of border.
            # Area is current window size (default).
            my_page.flick_by((0.3, 0.85, 0.5, 0.35))

            # Flick with ratio of border.
            # Area is ratio of current window size.
            my_page.flick_by((0.3, 0.85, 0.5, 0.35), (0.2, 0.2, 0.6, 0.8))

            # Flick with ratio of border.
            # Area is absolute coordinate.
            my_page.flick_by((0.3, 0.85, 0.5, 0.35), (100, 150, 300, 700))

            # Get absolute border coordinate by scrollable element rect.
            area = my_page.scrollable_element.rect
            my_page.flick_by((0.3, 0.85, 0.5, 0.35), area)
        """

        area = self.__get_area(area)
        offset = self.__get_offset(offset, area)

        for _ in range(times):
            driver = self.driver.flick(*offset)

        return driver

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
            window_x, window_y, window_width, window_height = self.get_window_rect().values()
            area_x = window_x + int(window_width * area_x)
            area_y = window_y + int(window_height * area_y)
            area_width = int(window_width * area_width)
            area_height = int(window_height * area_height)

        area = (area_x, area_y, area_width, area_height)
        logstack._logging(f'🟢 area: {area}')
        return area

    def __get_offset(
        self,
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

    def js_mobile_scroll_direction(self, direction: str = 'down'):
        """
        java script::

            # direction can be 'up', 'down', 'left', 'right'
            driver.execute_script('mobile: scroll', {'direction': direction})

        """
        return self.driver.execute_script('mobile: scroll', {'direction': direction})

    def draw_lines(self, dots: list[dict[str, int]], duration: int = 1000) -> None:
        """
        Appium 2.0 API.
        Draw lines by dots in given order.

        Args:
        - dots: A list of coordinates for the target dots, 
            e.g., [{'x': 100, 'y': 100}, {'x': 200, 'y': 200}, {'x': 300, 'y': 100}, ...].
        - duration: The time taken to draw between two points.
        """
        touch_input = PointerInput(interaction.POINTER_TOUCH, 'touch')
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=touch_input)

        # Press first dot, the first action can be executed without duration.
        actions.w3c_actions.pointer_action.move_to_location(dots[0]['x'], dots[0]['y'])
        actions.w3c_actions.pointer_action.pointer_down()

        # Start drawing.
        # Drawing needs duaration to execute the process.
        if duration < 250:
            # Follow by ActionBuilder duration default value.
            duration = 250
        actions.w3c_actions = ActionBuilder(self.driver, mouse=touch_input, duration=duration)
        for dot in dots[1:]:
            actions.w3c_actions.pointer_action.move_to_location(dot['x'], dot['y'])

        # relase = pointer_up, lift fingers off the screen.
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def draw_gesture(self, dots: list[dict[str, int]], gesture: str, duration: int = 1000) -> None:
        """
        Appium 2.0 API.
        Nine-box Gesture Drawing.

        Args:
        - dots: A list of coordinates for nine dots, which the position is:

            - 1,2,3
            - 4,5,6
            - 7,8,9

            you should set the dots following by order: [1,2,3,4,5,6,7,8,9],
            e.g. [{'x': 100, 'y': 100}, {'x': 200, 'y': 100}, {'x': 300, 'y': 100}, ...].

            If the nine points are elements,
            you can simply get the points by `my_page.my_elements.locations`.

        - gesture: A string containing the actual positions of the nine dots,
            such as '1235789' for drawing a Z shape.
        """
        touch_input = PointerInput(interaction.POINTER_TOUCH, 'touch')
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=touch_input)

        # Press first dot.
        # Not setting the duration here is because the first action can be executed without waiting.
        indexes = [(int(i) - 1) for i in gesture]
        press = indexes[0]
        actions.w3c_actions.pointer_action.move_to_location(dots[press]['x'], dots[press]['y'])
        actions.w3c_actions.pointer_action.pointer_down()

        # Start drawing.
        # Drawing needs duaration to execute the process.
        if duration < 250:
            duration = 250  # Follow by ActionBuilder duration default value.
        actions.w3c_actions = ActionBuilder(self.driver, mouse=touch_input, duration=duration)
        for draw in indexes[1:]:
            actions.w3c_actions.pointer_action.move_to_location(dots[draw]['x'], dots[draw]['y'])

        # relase = pointerup, lift fingers off the screen.
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def switch_to_active_element(self) -> WebElement:
        """
        Returns the element with focus, or BODY if nothing has focus.
        """
        return self.driver.switch_to.active_element

    def switch_to_alert(
        self,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> Alert | Literal[False]:
        """
        Switch to alert.
        """
        try:
            return self.wait(timeout).until(
                ec.alert_is_present(),
                f'Wait for alert to be present timed out after {timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def switch_to_default_content(self) -> None:
        """
        Switch focus to the default frame.
        """
        self.driver.switch_to.default_content()

    def switch_to_new_window(self, type_hint: str | None) -> None:
        """
        Switches to a new top-level browsing context.
        The type hint can be one of "tab" or "window".
        If not specified the browser will automatically select it.
        """
        self.driver.switch_to.new_window(type_hint)

    def switch_to_parent_frame(self) -> None:
        """
        Switches focus to the parent context.
        If the current context is the top level browsing context, the context remains unchanged.
        """
        self.driver.switch_to.parent_frame()

    def switch_to_window(self, window: str | int = 0) -> None:
        """
        selenium API
        Switches focus to the specified window.

        Args:
        - window:
            - str: Window name.
            - int: Window index.

        Usage::

            page.switch_to_window('main')
            page.switch_to_window(1)

        """
        if isinstance(window, int):
            window = self.driver.window_handles[window]
        self.driver.switch_to.window(window)

    def get_status(self) -> dict:
        """
        Appium API.
        Get the Appium server status

        Returns:
            Dict: The status information

        Usage::

            page.get_status()

        """
        return self.driver.get_status()

    @property
    def contexts(self) -> Any | list[str]:
        """
        appium API.
        Get current all contexts.
        """
        return self.driver.contexts

    def switch_to_context(self, context) -> AppiumWebDriver | Any:
        """
        appium API.
        Switch to NATIVE_APP or WEBVIEW.
        """
        return self.driver.switch_to.context(context)

    def switch_to_webview(
        self,
        switch: bool = True,
        index: int = -1,
        timeout: int | float | None = None,
        reraise: bool | None = None
    ) -> list[str] | Literal[False]:
        """
        Appium API.
        Wait for the webview is present and determine whether switch to it.

        Args:
        - switch: If True, switches to WEBVIEW when it becomes available; otherwise, does not switch.
        - index: Context index, defaulting to -1 which targets the latest WEBVIEW.
        - timeout: The timeout duration in seconds for explicit wait.
        - reraise: If True, re-raises a TimeoutException upon timeout; if False, returns False upon timeout.

        Returns:
        - contexts: ['NATIVE_APP', 'WEBVIEW_XXX', ...]
        - False: There is no any WEBVIEW in contexts.
        """
        try:
            return self.wait(timeout).until(
                ecex.webview_is_present(switch, index),
                f'Wait for WEBVIEW to be present timed out after {timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def switch_to_app(self) -> Any | str:
        """
        Appium API
        Switch to native app.

        Return: current context after judging whether to switch.
        """
        if self.driver.current_context != 'NATIVE_APP':
            self.driver.switch_to.context('NATIVE_APP')
        return self.driver.current_context

    def terminate_app(self, app_id: str, **options: Any) -> bool:
        """
        Appium API.
        Terminates the application if it is running.

        Args:
        - app_id: the application id to be terminates

        Keyword Args:
        - timeout (int): [Android only] how much time to wait for the uninstall to complete.
                500ms by default.

        Returns:
        - True if the app has been successfully terminated.
        """
        return self.driver.terminate_app(app_id, **options)

    def activate_app(self, app_id: str) -> AppiumWebDriver:
        """
        Appium API.
        Activates the application if it is not running
        or is running in the background.

        Args:
            app_id: the application id to be activated
        """
        return self.driver.activate_app(app_id)

    def save_screenshot(self, filename: Any) -> bool:
        """
        Saves a screenshot of the current window to a PNG image file.
        Returns False if there is any IOError, else returns True.
        Use full paths in your filename.

        Args:
        - filename: The full path you wish to save your screenshot to.
            This should end with a .png extension.

        Usage::

            driver.save_screenshot('/Screenshots/foo.png')

        """
        return self.driver.save_screenshot(filename)

    def switch_to_parent_frame(self) -> None:
        """
        Switches focus to the parent context.
        If the current context is the top level browsing context,
        the context remains unchanged.
        """
        self.driver.switch_to.parent_frame()

    def get_cookies(self) -> list[dict]:
        """
        Returns a set of dictionaries, corresponding to cookies visible in the current session.
        """
        return self.driver.get_cookies()

    def get_cookie(self, name: Any) -> dict | None:
        """
        Get a single cookie by name. Returns the cookie if found, None if not.
        """
        return self.driver.get_cookie(name)

    def add_cookie(self, cookie: dict) -> None:
        """
        Adds a cookie to your current session.

        Args:
        - cookie: A dictionary object
            - Required keys: "name" and "value"
            - optional keys: "path", "domain", "secure", "httpOnly", "expiry", "sameSite"

        Usage::

            page.add_cookie({'name' : 'foo', 'value' : 'bar'})
            page.add_cookie({'name' : 'foo', 'value' : 'bar', 'path' : '/'})
            page.add_cookie({'name' : 'foo', 'value' : 'bar', 'path' : '/', 'secure' : True})
            page.add_cookie({'name' : 'foo', 'value' : 'bar', 'sameSite' : 'Strict'})

        """
        self.driver.add_cookie(cookie)

    def add_cookies(self, cookies: list[dict]) -> None:
        """
        Adds cookies to your current session.

        Usage::

            cookies = [
                {'name' : 'foo', 'value' : 'bar'},
                {'name' : 'foo', 'value' : 'bar', 'path' : '/', 'secure' : True}},
                ...
            ]
            page.add_cookies(cookies)

        """
        if isinstance(cookies, list):
            for cookie in cookies:
                if isinstance(cookie, dict):
                    self.driver.add_cookie(cookie)
                else:
                    raise TypeError('Each cookie in cookies should be a dict.')
        else:
            raise TypeError('Cookies should be a list.')

    def delete_cookie(self, name) -> None:
        """
        Deletes a single cookie with the given name.
        """
        self.driver.delete_cookie(name)

    def delete_all_cookies(self) -> None:
        """
        Delete all cookies in the scope of the session.

        Usage::

            self.delete_all_cookies()

        """
        self.driver.delete_all_cookies()

    def switch_to_flutter(self) -> AppiumWebDriver | Any | None:
        """
        appium API.
        Switch to flutter app.
        """
        current_context = self.driver.current_context
        if current_context != "FLUTTER":
            return self.driver.switch_to.context('FLUTTER')

    def accept_alert(self) -> None:
        """
        selenium API.
        Accept an alert.
        """
        self.driver.switch_to.alert.accept()

    def dismiss_alert(self) -> None:
        """
        selenium API.
        Dismisses an alert.
        """
        self.driver.switch_to.alert.dismiss()

    @property
    def get_alert_text(self) -> str:
        """
        selenium API
        Gets the text of the Alert.
        """
        return self.driver.switch_to.alert.text

    def move_by_offset(self, xoffset, yoffset, perform: bool = True):
        """
        selenium API
        Moving the mouse to an offset from current mouse position.

        :Args:
         - x: X offset to move to, as a positive or negative integer.
         - y: Y offset to move to, as a positive or negative integer.
        """
        action = ActionChains(self.driver).move_by_offset(xoffset, yoffset)
        if not perform:
            return action
        action.perform()

    def implicitly_wait(self, timeout: int | float = 30) -> None:
        """
        implicitly wait.
        """
        self.driver.implicitly_wait(timeout)

    def set_script_timeout(self, time_to_wait: int | float) -> None:
        """
        Set the amount of time that the script should wait during an
           execute_async_script call before throwing an error.

        Usage::

            page.set_script_timeout(30)

        """
        self.driver.set_script_timeout(time_to_wait)

    def set_page_load_timeout(self, time_to_wait: int | float) -> None:
        """
        Set the amount of time to wait for a page load to complete
           before throwing an error.

        Usage::

            page.set_page_load_timeout(30)

        """
        self.driver.set_page_load_timeout(time_to_wait)

    def swipe_ratio(
        self,
        direction: str = SA.V,
        start: int = 75,
        end: int = 25,
        fix: int = None,
        ratio: bool = False,
        duration: int = 1000
    ) -> None:
        """
        Swipe by window ratio vertically or horizontally.

        Args:
        - dirtype:
            - vertical: 'vertical', 'v'
            - horizontal: 'horizontal', 'h'
        - start: Ratio of full screen size to start swiping.
        - end: Ratio of full screen size to stop swiping.
        - fix:
            - int: Fixed x or y coordinate or its proportion to the full screen
                when scrolling vertically or horizontally.
            - None: Fixed x or y coordinate default set to half of full screen.
        - fix_is_ratio: True, fixed coordination is proportion to the full screen, vice versa.
        - duration: defines the swipe speed as time taken to swipe from point a to point b, in ms.

        Usage::

            page.swipe_ratio('v', 80, 20)
            page.swipe_ratio('h', 80, 20)
            page.swipe_ratio('h', 80, 20, 100)
            page.swipe_ratio('h', 80, 20, 40, True)

        """
        # TODO deprecate
        warnings.warn(
            'This function is deprecated and will be removed in future versions. Please use "swipe_by" instead.',
            DeprecationWarning,
            stacklevel=2)

        vertical = 'v'
        horizontal = 'h'

        width, height = self.get_window_size().values()
        if direction.lower() in vertical:
            sx = ex = int(width / 2)
            sy = int(height * start / 100)
            ey = int(height * end / 100)
            if fix:
                if ratio:
                    sx = ex = int(width * fix / 100)
                else:
                    sx = ex = fix
        elif direction.lower() in horizontal:
            sy = ey = int(height / 2)
            sx = int(width * start / 100)
            ex = int(width * end / 100)
            if fix:
                if ratio:
                    sy = ey = int(height * fix / 100)
                else:
                    sy = ey = fix
        else:
            raise ValueError('Only accept dirtype: "v", "h"')
        self.driver.swipe(sx, sy, ex, ey, duration)
