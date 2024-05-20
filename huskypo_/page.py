# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# TODO selenium 4.0 and appium 2.0 methods.
# TODO Need to confirm the functional difference between 'driver' and 'page'.
# TODO Tracking the range using wait function.

from __future__ import annotations

from typing import Any, Literal, TypeAlias

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.print_page_options import PrintOptions

from . import logstack
from . import ec_extension as ecex
from .config import Timeout
from .swipe import SwipeBy, SwipeAction
from .swipe import SwipeActionMode as SAT
from .typing import AppiumWebDriver
from .typing import WebDriver, WebElement, WebDriverTuple

IntCoordinate: TypeAlias = dict[str, int] | tuple[int, int, int, int]
FloatCoordinate: TypeAlias = dict[str, float] | tuple[float, float, float, float]
TupleCoordinate: TypeAlias = tuple[int, int, int, int] | tuple[float, float, float, float]
Coordinate: TypeAlias = IntCoordinate | FloatCoordinate



class Page:

    def __init__(self, driver):
        if not isinstance(driver, WebDriverTuple):
            raise TypeError(f'The driver type should be "WebDriver", not {type(driver).__name__}.')
        self._driver: WebDriver = driver
        self._wait_timeout: int | float | None = None
        self._action = ActionChains(driver)

    @property
    def driver(self) -> WebDriver:
        return self._driver

    def wait(self, timeout: int | float | None = None):
        """
        Selenium and Appium API.
        Packing WebDriverWait(driver, timeout) to accept only the timeout parameter.

        Args:
        - timeout: Maximum time in seconds to wait for the expected condition.
        """
        self._wait_timeout = Timeout.DEFAULT if timeout is None else timeout
        return WebDriverWait(self.driver, self._wait_timeout)
    
    @property
    def action(self):
        """
        Calling instance of ActionChains.
        You can use it to perform an ActionChains method.

        Usage::
            
            page.action.scroll_to_element(element).click(element)
        """
        return self._action

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
        Refreshes the current page.
        """
        self.driver.refresh()

    def back(self) -> None:
        """
        Goes one step backward in the browser history.
        """
        self.driver.back()

    def forward(self) -> None:
        """
        Goes one step forward in the browser history.
        """
        self.driver.forward()

    def close(self) -> None:
        """
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

    def set_window_rect(self, x=None, y=None, width=None, height=None) -> dict | None:
        """
        selenium API
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
            return self.driver.set_window_rect(int(x), int(y), int(width), int(height))

    def get_window_rect(self) -> dict[str, int]:
        """
        Gets the x, y coordinates of the window as well as height and width of the current window.

        Return: {'x': int, 'y': int, 'width': int, 'height': int}
        """
        rect = self.driver.get_window_rect()
        return {key: rect[key] for key in ('x', 'y', 'width', 'height')}

    def set_window_position(
            self,
            x: int | float | str = 0,
            y: int | float | str = 0,
            windowHandle: str = 'current') -> dict:
        """
        selenium API
        Sets the x,y position of the current window. (window.moveTo)

        Args:
            - x: the x-coordinate in pixels to set the window position
            - y: the y-coordinate in pixels to set the window position

        Usage::

            page.set_window_position(0,0)

        """
        return self.driver.set_window_position(int(x), int(y), windowHandle)

    def get_window_position(self, windowHandle: str = "current") -> dict[str, int]:
        """
        Gets the x, y coordinates of the window as well as height and width of the current window.

        Return: {'x': int, 'y': int}
        """
        return self.driver.get_window_position(windowHandle)

    def set_window_size(
            self,
            width: int | float | str | None = None,
            height: int | float | str | None = None,
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
            self.driver.set_window_size(int(width), int(height), windowHandle)

    def get_window_size(self, windowHandle: str = 'current') -> dict[str, int]:
        """
        Gets the width and height of the current window.

        Return: {'width': int, 'height': int}
        """
        return self.driver.get_window_size(windowHandle)

    def get_window_border(self) -> dict[str, int]:
        """
        window border: {'left': int, 'right': int, 'top': int, 'bottom': int}
        """
        rect = self.driver.get_window_rect()
        left = rect['x']
        right = rect['x'] + rect['width']
        top = rect['y']
        bottom = rect['y'] + rect['height']
        return {'left': left, 'right': right, 'top': top, 'bottom': bottom}

    def get_window_center(self) -> dict[str, int]:
        """
        window center: {'x': x, 'y': y}
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

    def tap(self, positions: list[tuple[int, int]], duration: int | None = None) -> AppiumWebDriver:
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
            border: Coordinate = {'x': 0.0, 'y': 0.0, 'width': 1.0, 'height': 1.0},
            duration: int = 1000,
            times: int = 1
    ) -> AppiumWebDriver:
        """
        Swipe from one point to another point, which can customize offset and border setting.

        Args:
        - offset: The swiping range, which can be set as:
            - int: the absolute coordinate.
                - dict: {'start_x': int, 'start_y': int, 'end_x': int, 'end_y': int}
                - tuple: (int, int, int, int) follow as dict key.
            - float: the ratio of border (swipable range), and it should between 0.0 to 1.0.
                - dict: {'start_x': float, 'start_y': float, 'end_x': float, 'end_y': float}
                - tuple: (float, float, float, float) follow as dict key.
        - border: The swipable range, default is current window size, which can be set as:
            - int: the absolute rect.
                - dict: {'x': int, 'y': int, 'width': int, 'height': int}
                - tuple: (int, int, int, int) follow as dict key.
            - float: the ratio of current window size, and it should between 0.0 to 1.0.
                - dict: {'x': float, 'y': float, 'width': float, 'height': float}
                - tuple: (float, float, float, float) follow as dict key.
        - duration: defines the swipe speed as time taken to swipe from point a to point b, in ms,
                note that default set to 250 by ActionBuilder.
        - times: the swiping times.

        Usage::

            # Default is swiping down.
            # x: Fixed 50% (half) of current window width.
            # y: From 75% to 25% of current window height.
            my_page.swipe_by()

            # Swipe with customize absolute offset.
            # Note that the border parameter will not affect any swiping behavior.
            my_page.swipe_by((250, 300, 400, 700))

            # Swipe with ratio of border.
            # Border is current window size (default).
            my_page.swipe_by((0.3, 0.85, 0.5, 0.35))

            # Swipe with ratio of border.
            # Border is ratio of current window size.
            my_page.swipe_by((0.3, 0.85, 0.5, 0.35), (0.2, 0.2, 0.6, 0.8))

            # Swipe with ratio of border.
            # Border is absolute coordinate.
            my_page.swipe_by((0.3, 0.85, 0.5, 0.35), (100, 150, 300, 700))

            # Get absolute border coordinate by scrollable element rect.
            border = my_page.scrollable_element.rect
            my_page.swipe_by((0.3, 0.85, 0.5, 0.35), border)
        """

        border = self.__get_border(border)
        offset = self.__get_offset(offset, border)

        for _ in range(times):
            driver = self.driver.swipe(*offset, duration)

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
        
        if values_type == float and not all(0 <= value <= 1 for value in values):
            raise ValueError(f'All "{name}" values are floats and should be between "0.0" and "1.0".')
        
        return values

    def __get_border(self, border: TupleCoordinate) -> tuple[int, int, int, int]:

        border_x, border_y, border_width, border_height = self.__get_coordinate(border, 'border')

        if isinstance(border_width, float):
            window_x, window_y, window_width, window_height = self.get_window_rect().values()
            border_x = window_x + int(window_width * border_x)
            border_y = window_y + int(window_height * border_y)
            border_width = int(window_width * border_width)
            border_height = int(window_height * border_height)
        
        border = (border_x, border_y, border_width, border_height)
        logstack._logging(f'🟢 border: {border}')
        return border
    
    def __get_offset(self, 
            offset: TupleCoordinate, 
            border: tuple[int, int, int, int]
        ) -> tuple[int, int, int, int]:

        start_x, start_y, end_x, end_y = self.__get_coordinate(offset, 'offset')

        if isinstance(start_x, float):
            border_x, border_y, border_width, border_height = border
            start_x = border_x + int(border_width * start_x)
            start_y = border_y + int(border_height * start_y)
            end_x = border_x + int(border_width * end_x)
            end_y = border_y + int(border_height * end_y)
        
        offset = (start_x, start_y, end_x, end_y)
        logstack._logging(f'🟢 offset: {offset}')
        return offset
    
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

    def js_mobile_scroll_direction(self, direction: str = 'down'):
        """
        java script::

            # direction can be 'up', 'down', 'left', 'right'
            driver.execute_script('mobile: scroll', {'direction': direction})

        """
        return self.driver.execute_script('mobile: scroll', {'direction': direction})

    def draw_gesture(self, dots: list, gesture: str, duration: int = 1000) -> None:
        """
        Appium 2.0 API.
        Nine-box Gesture Drawing.

        Args:
        - dots: List of center coordinates of nine dots,
            e.g. [{'x1': x1, 'y1': y1}, {'x2': x2, 'y2': y2}, ...]
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
        appium API
        Switch to native app.

        Return: current context after judging whether to switch.
        """
        if self.driver.current_context != 'NATIVE_APP':
            self.driver.switch_to.context('NATIVE_APP')
        return self.driver.current_context

    def terminate_app(self, app_id) -> None:
        """
        Terminate the app to buffer, note that it does NOT shut down the app.

        Args:
        - app_id: app bundle id which like com.xxx.ooo.
        """
        self.driver.terminate_app(app_id)

    def activate_app(self, app_id) -> None:
        """
        Activate the app from buffer.

        Args:
        - app_id: app bundle id which like com.xxx.ooo.
        """
        self.driver.activate_app(app_id)

    def save_screenshot(self, filename: Any):
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
        self.driver.save_screenshot(filename)

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
