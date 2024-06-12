# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

from __future__ import annotations

from typing import Callable, Literal
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from .types import AppiumWebDriver, WebDriver, WebElement

# TODO difference between locator and WebElement
# locator: can using StaleElementReferenceException to retry to find element(s).
# WebElement: can NOT using StaleElementReferenceException to retry, for you can not get the locator by WebElement.


def _find_element_by(
    driver: WebDriver,
    locator: tuple[str, str],
    index: int | None
) -> WebElement:
    """
    index:
    - None: `driver.find_element(*locator)`
    - int: `driver.find_elements(*locator)[index]`,
        and treat `IndexError` as `NoSuchElementException`.
    """
    if index is None:
        return driver.find_element(*locator)
    try:
        return driver.find_elements(*locator)[index]
    except IndexError:
        raise NoSuchElementException


def presence_of_element_located(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement]:
    """
    Extended `presence_of_element_located`.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        return _find_element_by(driver, locator, index)

    return _predicate


def visibility_of_element_marked(
    mark: tuple[str, str] | WebElement,
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Package the `visibility_of_element_located` and `visibility_of_element` methods 
    to elastically execute the `wait_visible` process in the `Element` class.

    Args:
    - mark: (by, value) or WebElement.
    - locator: (by, value). This is used to avoid StaleElementReferenceException 
        when mark is a WebElement and retry by locator.
    - index:
        - None: Use driver.find_element(*locator).
        - int: Use driver.find_elements(*locator)[index].
    """

    def _predicate(driver: WebDriver):
        if isinstance(mark, tuple):
            return visibility_of_element_located(mark, index)(driver)
        else:
            try:
                return visibility_of_element(mark)(driver)
            except StaleElementReferenceException:
                return visibility_of_element_located(locator, index)(driver)

    return _predicate


def visibility_of_element_located(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `visibility_of_element_located`.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if element.is_displayed() else False
        except StaleElementReferenceException:
            return False

    return _predicate


def visibility_of_element(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `visibility_of`.
    StaleElementReferenceException is not caught here 
    because the element can only be re-located using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement
    """

    def _predicate(_):
        return element if element.is_displayed() else False

    return _predicate


def invisibility_of_element_marked(
    mark: tuple[str, str] | WebElement,
    index: int | None
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Extended `invisibility_of_element_located` and `invisibility_of_element`.
    There are two scenarios of invisibility, 
    which will be considered in the Element wait function:
    1. The element is present but not displayed.
    2. The element triggers a NoSuchElementException or StaleElementReferenceException, 
        which means the element is not present.

    Args:
    - mark: (by, value) or WebElement
    - index (if mark is locator): 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        target = mark
        try:
            if isinstance(target, tuple):
                target = _find_element_by(driver, target, index)
            return target if not target.is_displayed() else False
        except (NoSuchElementException, StaleElementReferenceException):
            return True

    return _predicate


def visibility_of_any_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement]]:
    """
    Extended `visibility_of_any_elements_located`.
    It can distinguish the return value of find_elements,
    if it is [], triggers NoSuchElementException.
    """
    # TODO Does it need negative condition?
    def _predicate(driver: WebDriver):
        elements = driver.find_elements(*locator)
        if elements == []:
            raise NoSuchElementException
        return [element for element in elements if element.is_displayed()]

    return _predicate


def element_located_to_be_clickable(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_clickable`.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if element.is_displayed() and element.is_enabled() else False
        except StaleElementReferenceException:
            return False

    return _predicate


def element_to_be_clickable(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_clickable`.
    StaleElementReferenceException is not caught here 
    because the element can only be re-located using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement
    """

    def _predicate(_):
        return element if element.is_displayed() and element.is_enabled() else False

    return _predicate


def element_marked_to_be_unclickable(
    mark: tuple[str, str] | WebElement,
    index: int | None
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Extended new function.
    There are two scenarios of unclickable element, 
    which will be considered in the Element wait function:
    1. The element is present but unclickable.
    2. The element triggers a NoSuchElementException or StaleElementReferenceException, 
        which means the element is not present.

    Args:
    - mark: (by, value) or WebElement
    - index (if mark is locator): 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        target = mark
        try:
            if isinstance(target, tuple):
                target = _find_element_by(driver, target, index)
            return target if not (target.is_displayed() and target.is_enabled()) else False
        except (NoSuchElementException, StaleElementReferenceException):
            return True

    return _predicate


def element_located_to_be_selected(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_located_to_be_selected`.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if element.is_selected() else False
        except StaleElementReferenceException:
            return False

    return _predicate


def element_to_be_selected(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_selected`.
    StaleElementReferenceException is not caught here 
    because the element can only be re-located using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement
    """

    def _predicate(_):
        return element if element.is_selected() else False

    return _predicate


def element_located_to_be_unselected(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended new function.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if not element.is_selected() else False
        except StaleElementReferenceException:
            return False

    return _predicate


def element_to_be_unselected(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended new function.
    StaleElementReferenceException is not caught here 
    because the element can only be re-located using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement
    """

    def _predicate(_):
        return element if not element.is_selected() else False

    return _predicate


def webview_is_present(
        switch: bool = True,
        index: int = -1
) -> Callable[[AppiumWebDriver], list[str] | Literal[False]]:
    """
    Wait for context WEBVIEW_XXX is present.
    """

    def _predicate(driver: AppiumWebDriver):
        contexts = driver.contexts
        if any('WEBVIEW' in context for context in contexts):
            if switch:
                context = contexts[index]
                driver.switch_to.context(context)
            return contexts
        return False

    return _predicate
