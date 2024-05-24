# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# TODO selenium 4.0 and appium 2.0 methods.
from __future__ import annotations

from typing import Literal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from . import logstack
from . import ec_extension as ecex
from .config import Timeout
from .by import ByAttribute
from .page import Page
from .typing import WebDriver, WebElement


class Elements:

    def __init__(
            self,
            by: str | None = None,
            value: str | None = None,
            timeout: int | float | None = None,
            remark: str | None = None):
        """
        Initial Elements attributes.

        Args:
        - by: The locator strategy. You can use all `By` methods as `from huskypo import By`.
        - value: The locator value.
        - timeout: Element timeout in seconds of explicit wait.
        - remark: Comments convenient for element identification, or logging.

        Usage (without parameter name)::

            # (by, value):
            elements = Elements(By.ACCESSIBILITY_ID, 'element_accid')

            # (by, value, timeout):
            elements = Elements(By.ACCESSIBILITY_ID, 'element_accid', 10)

            #(by, value, remark):
            elements = Elements(By.ACCESSIBILITY_ID, 'element_accid', 'these are xxx')

            # (by, value, timeout, remark):
            elements = Elements(By.ACCESSIBILITY_ID, 'element_accid', 10, 'these are xxx')

        """
        # (by, value)
        # Allowing `None` to initialize an empty descriptor for dynamic elements.
        if by not in ByAttribute.VALUES_WITH_NONE:
            raise ValueError(f'The locator strategy "{by}" is undefined.')
        if not isinstance(value, (str, type(None))):
            raise TypeError(f'The locator value type should be "str", not "{type(self.value).__name__}".')
        self.by = by
        self.value = value

        # (by, value, timeout)
        self._timeout = timeout
        # (by, value, remark)
        if not isinstance(timeout, (int, float, type(None))):
            remark = str(timeout)
            self._timeout = None

        # (by, value, timeout, remark)
        self.remark = remark
        if remark is None:
            self.remark = self.value

    def __get__(self, instance: Page, owner):
        # Dynamically obtain the page instance and 
        # execute the corresponding function only when needed.
        self._page = instance
        return self

    def __set__(self, instance: Page, value):
        # Setting element attribute values at runtime,
        # typically used for configuring dynamic elements.
        self.__init__(*value)

    @property
    def driver(self) -> WebDriver:
        return self._page._driver

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
    def timeout(self):
        """
        Get the initial timeout of the elements.
        """
        return Timeout.DEFAULT if self._timeout is None else self._timeout

    def test_attributes(self):
        """
        unit test
        """
        logstack.info(f'by               : {self.by}')
        logstack.info(f'value            : {self.value}')
        logstack.info(f'locator          : {self.locator}')
        logstack.info(f'timeout          : {self.timeout}')
        logstack.info(f'remark           : {self.remark}\n')

    def find_elements(self) -> list[WebElement]:
        """
        Using the traditional find_elements method 
        to locate elements without any waiting behavior.
        It is recommended for use in situations where no waiting is required.
        Note that if there are no any element found, 
        it will return empty list `[]`.
        """
        return self.driver.find_elements(*self.locator)

    def wait(self, timeout: int | float | None = None) -> WebDriverWait:
        """
        Selenium and Appium API.
        Packing WebDriverWait(driver, timeout) to accept only the timeout parameter.
        If you sets a timeout in here, it takes precedence;
        otherwise, it defaults to the timeout set for the element.

        Args:
        - timeout: Maximum time in seconds to wait for the expected condition.
        """
        self._wait_timeout = self.timeout if timeout is None else timeout
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
            index: int | None = None,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> list[WebElement] | WebElement | Literal[False]:
        """
        Selenium and Appium API.
        Wait for the element or elements to be `present`.

        Args:
        - index:
            - int: It will returns an element by list index of elements.
            - None: It will returns all elements.
        - timeout: Maximum time in seconds to wait for the element or elements to become present.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - list[WebElement]: All elements when index is None.
        - WebElement: Element by list index of elements when index is int.
        - False: No any element is present.
        """
        elements = self.wait_all_present(timeout, reraise)
        if index is not None:
            try:
                return elements[index]
            except TypeError:
                # Catch TypeError: False[index].
                # We reraise TimeoutException to indicate that elements are not present after timeout.
                raise TimeoutException(
                    f'All elements {self.remark} are not present timed out after {self._wait_timeout} seconds.')
        return elements

    def wait_all_present(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> list[WebElement] | Literal[False]:
        """
        Selenium and Appium API.
        Wait for `at least one element` to be `present`.

        Args:
        - timeout: Maximum time in seconds to wait for at least one element to become present.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - list[WebElement]: At least one element is present before timeout.
        - False: No any element is present after timeout.
        """
        try:
            return self.wait(timeout).until(
                ec.presence_of_all_elements_located(self.locator),
                f'Wait for all elements {self.remark} to be present timed out after {self._wait_timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_all_not_present(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium and Appium API.
        Wait for `all elements` to be `NOT present`.

        Args:
        - timeout: Maximum time in seconds to wait for all elements to become not present.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - True: All elements are not present before timeout.
        - False: At least one element is still present after timeout.
        """
        try:
            self.wait(timeout).until_not(
                ec.presence_of_all_elements_located(self.locator),
                f'Wait for all elements {self.remark} to be not present timed out after {self._wait_timeout} seconds.')
            return True
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_any_visible(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> list[WebElement] | Literal[False]:
        """
        Selenium and Appium API.
        Wait for `at least one element` to be `visible`.

        Args:
        - timeout: Maximum time in seconds to wait for at least one element to become visible.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - list[WebElement]: At least one element is visible before timeout.
        - False: No any element is visible after timeout.
        """
        try:
            return self.wait(timeout).until(
                ecex.visibility_of_any_elements_located(self.locator),
                f'Wait for any elements {self.remark} to be visible timed out after {self._wait_timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_all_not_visible(
            self,
            timeout: int | float | None = None,
            present: bool = True,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium and Appium API.
        Wait for `all elements` to be `not visible`.
        Note that the official method also accommodates the `not present` status,
        as find_elements will not trigger a NoSuchElementException
        but instead return an empty list when no elements are found.

        Args:
        - timeout: Maximum time in seconds to wait for all elements to become not visible.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - True: All elements are not visible before timeout.
        - False: At least one element is visible after timeout.
        """
        try:
            result = self.wait(timeout).until_not(
                ecex.visibility_of_any_elements_located(self.locator),
                f'Wait for all elements {self.remark} to be not visible timed out after {self._wait_timeout} seconds.')
            if result and present:
                return None
            return True
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_all_visible(
            self,
            timeout: int | float | None = None,
            reraise: bool | None = None
    ) -> list[WebElement] | Literal[False]:
        """
        Selenium and Appium API.
        Wait for `all elements` to be `visible`.

        Args:
        - timeout: Maximum time in seconds to wait for all elements to become visible.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - list[WebElement]: All elements are visible before timeout.
        - False: At least one element is not visible after timeout.
        """
        try:
            return self.wait(timeout).until(
                ec.visibility_of_all_elements_located(self.locator),
                f'Wait for all elements {self.remark} to be visible timed out after {self._wait_timeout} seconds.')
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def wait_any_not_visible(
            self,
            timeout: int | float | None = None,
            present: bool = True,
            reraise: bool | None = None
    ) -> bool:
        """
        Selenium and Appium API.
        Wait for `at least one element` to be `not visible`.
        Note that the official method has two possible outcomes,
        we can distinguish between these two results based on these statuses:
        - []: An empty list, indicating that no elements were found by find_elements.
        - False: Signifying that at least one element exists but is not visible.

        Args:
        - timeout: Maximum time in seconds to wait for at least one element to become not visible.
        - reraise: True means reraising TimeoutException; vice versa.

        Returns:
        - True: At least one element is not visible before timeout.
        - False: All elements are visible after timeout.
        """
        try:
            result = self.wait(timeout).until_not(
                ec.visibility_of_all_elements_located(self.locator),
                f'Wait for any elements {self.remark} to be not visible timed out after {self._wait_timeout} seconds.')
            if result == [] and present:
                # []: No elements were found by find_elements.
                return None
            return True
        except TimeoutException:
            if Timeout.reraise(reraise):
                raise
            return False

    def are_all_present(self, timeout: int | float | None = None) -> bool:
        """
        Selenium and Appium API.
        Whether the all elements are present.

        Args:
        - timeout: Maximum time in seconds to wait for the element to become present.

        Returns:
        - True: All the elements are present before timeout.
        - False: All the elements are still not present after timeout.
        """
        return True if self.wait_all_present(timeout, False) else False

    def are_all_visible(self):
        """
        Selenium and Appium API.
        Whether all the elements are visible.

        Returns:
        - True: All the elements are visible.
        - False: At least one element is not visible.
        """
        elements = self.wait_all_present(reraise=True)
        for element in elements:
            if not element.is_displayed():
                return False
        return True

    def are_any_visible(self):
        """
        Selenium and Appium API.
        Whether at least one element is visible.

        Returns:
        - True: At least one element is visible.
        - False: All the elements are not visible.
        """
        elements = self.wait_all_present(reraise=True)
        return True if [element for element in elements if element.is_displayed()] else False

    @property
    def quantity(self):
        """
        Selenium and Appium API.
        Get the quantity of elements.
        """
        try:
            return len(self.wait_all_present(reraise=True))
        except TimeoutException:
            return 0

    @property
    def texts(self) -> list[str]:
        """
        Selenium and Appium API.
        Gets texts of all present elements.
        """
        elements = self.wait_all_present(reraise=True)
        return [element.text for element in elements]

    @property
    def all_visible_texts(self) -> list[str]:
        """
        Selenium and Appium API.
        Gets texts of all visible elements.
        """
        elements = self.wait_all_visible(reraise=True)
        return [element.text for element in elements]

    @property
    def any_visible_texts(self) -> list[str]:
        """
        Selenium and Appium API.
        WebElements: find_elements(by, value)
        Gets texts of `at least one` visible element.
        """
        elements = self.wait_any_visible(reraise=True)
        return [element.text for element in elements]

    @property
    def rects(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets locations relative to the view and size of all elements.\n
        """
        elements = self.wait_all_present(reraise=True)
        result = [{'x': rect['x'], 'y': rect['y'], 'width': rect['width'], 'height': rect['height']}
                  for element in elements
                  for rect in [element.rect]]
        return result

    @property
    def locations(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets locations of all elements.
        """
        elements = self.wait_all_present(reraise=True)
        return [element.location for element in elements]

    @property
    def sizes(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets sizes of all elements.
        Note that it will rearrange size to {'width': width, 'height': height}
        """
        elements = self.wait_all_present(reraise=True)
        result = [{'width': size['width'], 'height': size['height']}
                  for element in elements
                  for size in [element.size]]
        return result

    @property
    def centers(self) -> list[dict[str, int]]:
        """
        Selenium and Appium API.
        Gets center locations relative to the view of all elements.
        """
        elements = self.wait_all_present(reraise=True)
        result = [{'x': int(rect['x'] + rect['width'] / 2),
                   'y': int(rect['y'] + rect['height'] / 2)}
                  for element in elements
                  for rect in [element.rect]]
        return result

    def get_attributes(self, name: str) -> list[str | dict | None]:
        """
        Selenium and Appium API.
        Gets specific attributes or properties of all elements.
        """
        elements = self.wait_all_present(reraise=True)
        return [element.get_attribute(name) for element in elements]

    def get_properties(self, name: str) -> list[WebElement | bool | dict | str]:
        """
        Selenium API.
        Gets specific properties of all elements.
        """
        elements = self.wait_all_present(reraise=True)
        return [element.get_property(name) for element in elements]

    @property
    def locations_in_view(self) -> list[dict[str, int]]:
        """
        Appium API.
        Gets locations relative to the view of all elements.
        """
        elements = self.wait_all_present(reraise=True)
        return [element.location_in_view for element in elements]
