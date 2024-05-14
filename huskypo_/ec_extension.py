from __future__ import annotations

from typing import Callable, Literal
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from huskypo_.typing import AppiumWebDriver, WebDriver, WebElement


def presence_of_element_located(
        locator: tuple[str, str],
        index: int | None
) -> Callable[[WebDriver], WebElement]:
    """
    We expanded the original expected_conditions `presence_of_element_located` method,
    allowing the use of `driver.find_elements(*locator)[index]` to perform explicit wait.
    """

    def _predicate(driver: WebDriver):
        if index is not None:
            try:
                return driver.find_elements(*locator)[index]
            except IndexError:
                # Due to find_elements not throwing any exceptions,
                # we treat an IndexError as a NoSuchElementException,
                # it will trigger ignored_exception process in until and until_not method.
                raise NoSuchElementException
        return driver.find_element(*locator)

    return _predicate


def visibility_of_element_located(
        locator: tuple[str, str],
        index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    We expanded the original expected_conditions `visibility_of_element_located` method,
    allowing the use of `driver.find_elements(*locator)[index]` to perform explicit wait.
    """

    def _predicate(driver: WebDriver):
        try:
            if index is None:
                # avoid to call both find method when index is not none.
                element = driver.find_element(*locator)
            else:
                try:
                    element = driver.find_elements(*locator)[index]
                except IndexError:
                    # Due to find_elements not throwing any exceptions,
                    # we treat an IndexError as a NoSuchElementException,
                    # it will trigger ignored_exception process in until and until_not method.
                    raise NoSuchElementException
            return element if element.is_displayed() else False
        except StaleElementReferenceException:
            return False

    return _predicate


def visibility_of_any_elements_located(
        locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement]]:
    """
    We are reconstructing the official visibility_of_any_elements_located method 
    to enable it to distinguish whether the return value [] 
    indicates that all elements are either not present or not visible.
    """

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
    We referenced the official `element_to_be_clickable` method
    and named it `element_located_to_be_clickable` to restrict users
    to only use locator for providing element information,
    and allowing the use of `driver.find_elements(*locator)[index]` to perform explicit wait.
    """

    def _predicate(driver: WebDriver):
        try:
            if index is None:
                # avoid to call both find method when index is not none.
                element = driver.find_element(*locator)
            else:
                try:
                    element = driver.find_elements(*locator)[index]
                except IndexError:
                    # Due to find_elements not throwing any exceptions,
                    # we treat an IndexError as a NoSuchElementException,
                    # it will trigger ignored_exception process in until and until_not method.
                    raise NoSuchElementException
            return element if element.is_displayed() and element.is_enabled() else False
        except StaleElementReferenceException:
            return False

    return _predicate


def element_located_to_be_selected(
        locator: tuple[str, str],
        index: int | None
) -> Callable[[WebDriver], bool]:
    """
    We expanded the original expected_conditions `element_located_to_be_selected` method,
    allowing the use of `driver.find_elements(*locator)[index]` to perform explicit wait.
    """

    def _predicate(driver: WebDriver):
        if index is not None:
            try:
                return driver.find_elements(*locator)[index].is_selected()
            except IndexError:
                # Due to find_elements not throwing any exceptions,
                # we treat an IndexError as a NoSuchElementException,
                # it will trigger ignored_exception process in until and until_not method.
                raise NoSuchElementException
        return driver.find_element(*locator).is_selected()

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
