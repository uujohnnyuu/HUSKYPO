# Author: Johnny Chou
# Email: johnny071531@gmail.com
# PyPI: https://pypi.org/project/huskypo/
# GitHub: https://github.com/uujohnnyuu/huskyPO

from typing import TypeAlias

from selenium.webdriver.remote.webdriver import WebDriver as SeleniumWebDriver
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
from appium.webdriver.webelement import WebElement as AppiumWebElement

WebDriver: TypeAlias = SeleniumWebDriver | AppiumWebDriver
WebElement: TypeAlias = SeleniumWebElement | AppiumWebElement

WebDriverTuple = (SeleniumWebDriver, AppiumWebDriver)
WebElementTuple = (SeleniumWebElement, AppiumWebElement)
