# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

from __future__ import annotations

from typing import Callable, Literal
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from .types import AppiumWebDriver, WebDriver, WebElement


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
    else:
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


def visibility_of_element(
        mark: tuple[str, str] | WebElement,
        index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `visibility_of_element_located` and `visibility_of`.

    Args:
    - mark: (by, value) or WebElement
    - index (if mark is locator): 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        target = mark
        if isinstance(target, tuple):
            target = _find_element_by(driver, target, index)
        return target if target.is_displayed() else False

    return _predicate


def invisibility_of_element(
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


def element_to_be_clickable(
    mark: tuple[str, str] | WebElement,
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_clickable`.

    Args:
    - mark: (by, value) or WebElement
    - index (if mark is locator): 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        try:
            target = mark
            if isinstance(target, tuple):
                target = _find_element_by(driver, target, index)
            return target if target.is_displayed() and target.is_enabled() else False
        except StaleElementReferenceException:
            # TODO
            pass

    return _predicate


def element_to_be_unclickable(
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


def element_to_be_selected(
    mark: tuple[str, str] | WebElement,
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_located_to_be_selected` and `element_to_be_selected`.

    Args:
    - mark: (by, value) or WebElement
    - index (if mark is locator): 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        target = mark
        if isinstance(target, tuple):
            target = _find_element_by(driver, target, index)
        return target if target.is_selected() else False

    return _predicate


def element_to_be_unselected(
    mark: tuple[str, str] | WebElement,
    index: int | None
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Extended new function.
    Note that unselected is different from conditions like invisible and unclickable. 
    The selected or unselected state depends on the user's action, 
    so the element must be present. 
    Therefore, we do not accept NoSuchElementException or StaleElementReferenceException.

    Args:
    - mark: (by, value) or WebElement
    - index (if mark is locator): 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    """

    def _predicate(driver: WebDriver):
        target = mark
        if isinstance(target, tuple):
            target = _find_element_by(driver, target, index)
        return target if not target.is_selected() else False

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
