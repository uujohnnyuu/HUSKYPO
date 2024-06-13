# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

# All you need to know about this expected conditions extension (referred to as ECEX):

# 1. ECEX extends all methods related to element states, 
# including present, visible, clickable, selected, and their opposites.

# 2. You can perform explicit waits using find_elements(*locator)[index]. 
# We have designed it to detect NoSuchElementException.

# 3. From the official methods, we know that explicit waits can be 
# performed using either locators or WebElements. 
# Some methods, like those related to visibility, are separate; 
# others, like those related to clickability, are integrated.

# 4. ECEX separates the methods for locators and WebElements 
# because these two approaches should handle exceptions differently, 
# allowing for more comprehensive exception handling.

# 5. For inverse states, invisible and unclickable can be set to include the absent state. 
# However, unselected requires the element to be present 
# because this state is highly related to user interaction, 
# and the element must be present to be meaningful.

# 6. ECEX methods related to marked elements are 
# mainly used in wait-related functions within the Element class. 
# Please consider their feasibility before use.

from __future__ import annotations

from typing import Callable, Literal

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

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
    Whether the element is present.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is present.
    """

    def _predicate(driver: WebDriver):
        return _find_element_by(driver, locator, index)

    return _predicate


def absence_of_element_located(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], bool]:
    """
    Whether the element is absent.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - True: The element is absent.
    - False: The element is present.
    """

    def _predicate(driver: WebDriver):
        try:
            _find_element_by(driver, locator, index)
            return False
        except NoSuchElementException:
            return True

    return _predicate


def presence_of_any_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement]]:
    """
    Extended `presence_of_all_elements_located`.
    Whether there are `any (at least one)` elements can be found by the locator.
    Note that "all" is changed to "any" because the logic of `find_elements` 
    is to find `at least one matched elements`.

    Args:
    - locator: (by, value)
    """

    def _predicate(driver: WebDriver):
        return driver.find_elements(*locator)

    return _predicate


def absence_of_all_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], bool]:
    """
    Whether `all the elements are absent` by the locator.
    Note that this is `completely opposite to presence_of_all_elements_located`.

    Args:
    - locator: (by, value)
    """

    def _predicate(driver: WebDriver):
        if driver.find_elements(*locator) == []:
            return True
        return False

    return _predicate


def visibility_of_element_marked(
    mark: tuple[str, str] | WebElement,
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    This is for the `wait_visible` method of the `Element` class.

    We combine the `visibility_of_element_located` and `visibility_of_element` methods 
    to flexibly execute the corresponding waiting process.

    Args:
    - mark: (by, value) or WebElement.
    - locator: (by, value). This is used to avoid StaleElementReferenceException 
        when mark is a WebElement and retry by this locator.
    - index:
        - None: Use driver.find_element(*locator).
        - int: Use driver.find_elements(*locator)[index].
    
    Return process:
    - `visibility_of_element_located`:
        - "mark" is a locator.
        - Executed by "locator" when "mark" is a WebElement and 
            triggers a StaleElementReferenceException in the `visibility_of_element` process.
    - `visibility_of_element`: "mark" is a WebElement.
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
    Whether the element is visible.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is visible.
    - False: The element is present and invisible, or absent.
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if element.is_displayed() else False
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    return _predicate


def visibility_of_element(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `visibility_of`.
    Whether the element is visible.

    We do not catch StaleElementReferenceException here (the same as official ec) because 
    the element can only be relocated using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is visible.
    - False: The element is present and invisible.
    """

    def _predicate(_):
        return element if element.is_displayed() else False

    return _predicate


def invisibility_of_element_marked(
    mark: tuple[str, str] | WebElement,
    locator: tuple[str, str],
    index: int | None,
    present: bool = True
) -> Callable[[WebDriver], WebElement | bool]:
    """
    This is for the `wait_invisible` method of the `Element` class.

    We combine the `invisibility_of_element_located` and `invisibility_of_element` methods 
    to flexibly execute the corresponding waiting process.

    Args:
    - mark: (by, value) or WebElement.
    - locator: (by, value). This is used to avoid StaleElementReferenceException 
        when mark is a WebElement and retry by this locator.
    - index:
        - None: Use driver.find_element(*locator).
        - int: Use driver.find_elements(*locator)[index].
    - present: Whether element should be present or not.
        - True: Element should be `present and invisible`.
        - False: Element can be absent.

    Return process:
    - `invisibility_of_element_located`:
        - "mark" is a locator.
        - Executed by "locator" when "mark" is a WebElement and 
            triggers a StaleElementReferenceException in the `invisibility_of_element` process.
    - invisibility_of_element: "mark" is a WebElement.
    """

    def _predicate(driver: WebDriver):
        if isinstance(mark, tuple):
            return invisibility_of_element_located(mark, index, present)(driver)
        else:
            try:
                return invisibility_of_element(mark)(driver)
            except StaleElementReferenceException:
                if present:
                    return invisibility_of_element_located(locator, index, present)(driver)
                return True

    return _predicate


def invisibility_of_element_located(
    locator: tuple[str, str],
    index: int | None,
    present: bool = True
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Extended `invisibility_of_element_located`.
    Whether the element is present and invisible, or absent.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    - present: Whether element should be present or not.
        - True: Element should be `present and invisible`.
        - False: Element can be absent.

    Return:
    - WebElement: The element is `present and invisible`.
    - False: 
        - The element is `present and visible`.
        - The element is `absent and should be present` ("present" is True).
    - True: The element is `absent and allowed` ("present" is False).
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if not element.is_displayed() else False
        except (NoSuchElementException, StaleElementReferenceException):
            return False if present else True

    return _predicate


def invisibility_of_element(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `invisibility_of_element`.
    Whether the element is present and invisible.

    We do not catch StaleElementReferenceException here (the same as official ec) because 
    the element can only be relocated using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is present and invisible.
    - False: The element is present and visible.
    """

    def _predicate(_):
        return element if not element.is_displayed() else False

    return _predicate

# TODO
def visibility_of_any_elements_located(
    locator: tuple[str, str]
) -> Callable[[WebDriver], list[WebElement]]:
    """
    Extended `visibility_of_any_elements_located`.
    Whether any elements are visible. 
    It can distinguish the return value of find_elements,
    if it is [], triggers NoSuchElementException.

    Args:
    - locator: (by, value)
    """

    def _predicate(driver: WebDriver):
        elements = driver.find_elements(*locator)
        if elements == []:
            raise NoSuchElementException
        return [element for element in elements if element.is_displayed()]

    return _predicate


# def invisibility_of_all_elements_located(
#     locator: tuple[str, str],
#     present: bool = True
# ) -> Callable[[WebDriver], list[WebElement]]:
#     """
#     """
    
#     def _predicate(driver: WebDriver):
#         elements = driver.find_elements(*locator)
#         if elements == []:
#             raise NoSuchElementException
#         return [element for element in elements if element.is_displayed()]

#     return _predicate


def element_marked_to_be_clickable(
    mark: tuple[str, str] | WebElement,
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    This is for the `wait_clickable` method of the `Element` class.

    We combine the `element_located_to_be_clickable` and `element_to_be_clickable` methods 
    to flexibly execute the corresponding waiting process.

    Args:
    - mark: (by, value) or WebElement.
    - locator: (by, value). This is used to avoid StaleElementReferenceException 
        when mark is a WebElement and retry by this locator.
    - index:
        - None: Use driver.find_element(*locator).
        - int: Use driver.find_elements(*locator)[index].
    
    Return process:
    - `element_located_to_be_clickable`:
        - "mark" is a locator.
        - Executed by "locator" when "mark" is a WebElement and 
            triggers a StaleElementReferenceException in the `element_to_be_clickable` process.
    - element_to_be_clickable: "mark" is a WebElement.
    """

    def _predicate(driver: WebDriver):
        if isinstance(mark, tuple):
            return element_located_to_be_clickable(mark, index)(driver)
        else:
            try:
                return element_to_be_clickable(mark)(driver)
            except StaleElementReferenceException:
                return element_located_to_be_clickable(locator, index)(driver)

    return _predicate


def element_located_to_be_clickable(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_clickable`.
    Whether the element is clickable.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is clickable.
    - False: The element is present and unclickable, or absent.
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if element.is_displayed() and element.is_enabled() else False
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    return _predicate


def element_to_be_clickable(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_to_be_clickable`.
    Whether the element is clickable.

    We do not catch StaleElementReferenceException here (the same as official ec) because 
    the element can only be relocated using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is clickable.
    - False: The element is present and unclickable.
    """

    def _predicate(_):
        return element if element.is_displayed() and element.is_enabled() else False

    return _predicate


def element_marked_to_be_unclickable(
    mark: tuple[str, str] | WebElement,
    locator: tuple[str, str],
    index: int | None,
    present: bool = True
) -> Callable[[WebDriver], WebElement | bool]:
    """
    This is for the `wait_unclickable` method of the `Element` class.

    We combine the `element_located_to_be_unclickable` and `element_to_be_unclickable` methods 
    to flexibly execute the corresponding waiting process.

    Args:
    - mark: (by, value) or WebElement.
    - locator: (by, value). This is used to avoid StaleElementReferenceException 
        when mark is a WebElement and retry by this locator.
    - index:
        - None: Use driver.find_element(*locator).
        - int: Use driver.find_elements(*locator)[index].
    - present: Whether element should be present or not.
        - True: Element should be `present and invisible`.
        - False: Element can be absent.

    Return process:
    - element_located_to_be_unclickable:
        - "mark" is a locator.
        - Executed by "locator" when "mark" is a WebElement and 
            triggers a StaleElementReferenceException in the `element_to_be_unclickable` process.
    - element_to_be_unclickable: "mark" is a WebElement.
    """

    def _predicate(driver: WebDriver):
        if isinstance(mark, tuple):
            return element_located_to_be_unclickable(mark, index, present)(driver)
        else:
            try:
                return element_to_be_unclickable(mark)(driver)
            except StaleElementReferenceException:
                if present:
                    return element_located_to_be_unclickable(locator, index, present)(driver)
                return True

    return _predicate


def element_located_to_be_unclickable(
    locator: tuple[str, str],
    index: int | None,
    present: bool = True
) -> Callable[[WebDriver], WebElement | bool]:
    """
    Whether the element is present and unclickable, or absent.
    
    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]
    - present: Whether element should be present or not.
        - True: Element should be `present and unclickable`.
        - False: Element can be absent.

    Return:
    - WebElement: The element is `present and unclickable`.
    - False: 
        - The element is `present and clickable`.
        - The element is `absent and should be present` ("present" is True).
    - True: The element is `absent and allowed` ("present" is False).
    """

    def _predicate(driver: WebDriver):
        try:
            element = _find_element_by(driver, locator, index)
            return element if not(element.is_displayed() and element.is_enabled()) else False
        except (NoSuchElementException, StaleElementReferenceException):
            return False if present else True

    return _predicate


def element_to_be_unclickable(
    element: WebElement
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is present and unclickable.

    We do not catch StaleElementReferenceException here (the same as official ec) because 
    the element can only be relocated using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is present and unclickable.
    - False: The element is present and clickable.
    """

    def _predicate(_):
        return element if not (element.is_displayed() and element.is_enabled()) else False

    return _predicate


def element_marked_to_be_selected(
    mark: tuple[str, str] | WebElement,
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    This is for the `wait_selected` method of the `Element` class.

    We combine the `element_located_to_be_selected` and `element_to_be_selected` methods 
    to flexibly execute the corresponding waiting process.

    Args:
    - mark: (by, value) or WebElement.
    - locator: (by, value). This is used to avoid StaleElementReferenceException 
        when mark is a WebElement and retry by this locator.
    - index:
        - None: Use driver.find_element(*locator).
        - int: Use driver.find_elements(*locator)[index].
    
    Return process:
    - element_located_to_be_selected:
        - "mark" is a locator.
        - Executed by "locator" when "mark" is a WebElement and 
            triggers a StaleElementReferenceException in the `element_to_be_selected` process.
    - element_to_be_selected: "mark" is a WebElement.
    """

    def _predicate(driver: WebDriver):
        if isinstance(mark, tuple):
            return element_located_to_be_selected(mark, index)(driver)
        else:
            try:
                return element_to_be_selected(mark)(driver)
            except StaleElementReferenceException:
                return element_located_to_be_selected(locator, index)(driver)

    return _predicate


def element_located_to_be_selected(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Extended `element_located_to_be_selected`.
    Whether the element is selected.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is selected.
    - False: The element is present and unselected, or absent.
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
    Whether the element is selected.

    We do not catch StaleElementReferenceException here (the same as official ec) because 
    the element can only be relocated using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is selected.
    - False: The element is present and unselected.
    """

    def _predicate(_):
        return element if element.is_selected() else False

    return _predicate


def element_marked_to_be_unselected(
    mark: tuple[str, str] | WebElement,
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    This is for the `wait_unselected` method of the `Element` class.

    We combine the `element_located_to_be_unselected` and `element_to_be_unselected` methods 
    to flexibly execute the corresponding waiting process.

    Args:
    - mark: (by, value) or WebElement.
    - locator: (by, value). This is used to avoid StaleElementReferenceException 
        when mark is a WebElement and retry by this locator.
    - index:
        - None: Use driver.find_element(*locator).
        - int: Use driver.find_elements(*locator)[index].
    
    Return process:
    - element_located_to_be_unselected:
        - "mark" is a locator.
        - Executed by "locator" when "mark" is a WebElement and 
            triggers a StaleElementReferenceException in the `element_to_be_unselected` process.
    - element_to_be_unselected: "mark" is a WebElement.
    """

    def _predicate(driver: WebDriver):
        if isinstance(mark, tuple):
            return element_located_to_be_unselected(mark, index)(driver)
        else:
            try:
                return element_to_be_unselected(mark)(driver)
            except StaleElementReferenceException:
                return element_located_to_be_unselected(locator, index)(driver)

    return _predicate


def element_located_to_be_unselected(
    locator: tuple[str, str],
    index: int | None
) -> Callable[[WebDriver], WebElement | Literal[False]]:
    """
    Whether the element is presnet and unselected.

    Args:
    - locator: (by, value)
    - index: 
        - None: driver.find_element(*locator)
        - int: driver.find_elements(*locator)[index]

    Return:
    - WebElement: The element is unselected.
    - False: The element is present and selected, or absent.
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
    Whether the element is presnet and unselected.

    We do not catch StaleElementReferenceException here (the same as official ec) because 
    the element can only be relocated using the locator. 
    Therefore, if you need to handle stale element issues, 
    it must be done in an external function.

    Args:
    - element: WebElement

    Return:
    - WebElement: The element is unselected.
    - False: The element is present and selected.
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
