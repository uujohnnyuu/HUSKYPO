from huskypo import Page, Element, Elements
from huskypo import By
from huskypo import dynamic


class MyPage(Page):

    # There is no need to include the init function in your pages.
    # This is used to bypass driver type verification in example.
    def __init__(self, driver):
        self._driver = driver

    # Static Element.
    element_by_value = Element(By.ID, 'value')
    element_by_value_index = Element(By.ID, 'value', 0)
    element_by_value_remark = Element(By.ID, 'value', 'this is remark')
    element_by_value_index_timeout = Element(By.ID, 'value', -1, 99)
    element_by_value_index_remark = Element(By.ID, 'value', -1, 'this is remark')
    element_by_value_index_timeout_remark = Element(By.ID, 'value', -1, 99, 'this is remark')

    # Static Elements.
    elements_by_value = Elements(By.ID, 'value')
    elements_by_value_timeout = Elements(By.ID, 'value', 10)
    elements_by_value_remark = Elements(By.ID, 'value', 'this is remark')
    elements_by_value_timeout_remark = Elements(By.ID, 'value', 30, 'this is remark')

    # Page objects are typically set up with static methods and attribute values,
    # so the element instances represent the usual way of defining elements.
    # However, if there is a development scenario that necessitates the use of dynamic positioning,
    # where attribute values need to be determined during the execution of test cases,
    # the following method for dynamically setting element positions can be used.

    # Dynamic Element(s) by "dynamic" decorator.
    # This is recommended simplified approach.
    @dynamic
    def d_element(self, par: str):
        return Element(By.ID, f'ID_{par}', None, 99, 'this is dynamic element by decorator')

    @dynamic
    def d_elements(self, par: str):
        return Elements(By.ACCESSIBILITY_ID, f'ACCID_{par}', 99, 'this is dynamic elements by decorator')

    # Dynamic Element(s) by descriptor
    # This is the standard notation for descriptor assignment.
    static_element = Element()

    def dynamic_element(self, par: str) -> Element:
        self.static_element = (By.ID, f'value_{par}')  # call __set__
        return self.static_element

    static_elements = Elements()

    def dynamic_elements(self, par: str) -> Elements:
        self.static_elements = (By.ACCESSIBILITY_ID, f'value_{par}')  # call __set__
        return self.static_elements
