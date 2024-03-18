from huskypo import By, Page, Element, Elements
from huskypo.decorator import dynamic


class MyPage(Page):

    # Skip checking driver type.
    def __init__(self, driver):
        self._driver = driver

    # dynamic decorator
    @dynamic
    def d_element(self, par: str):
        return Element(By.ID, f'ID_{par}', 10, 99, 'this is dynamic element by decorator')

    @dynamic
    def d_elements(self, par: str):
        return Elements(By.ACCESSIBILITY_ID, f'ACCID_{par}', 199, 'this is dynamic elements by decorator')

    # static Element
    element_by_value = Element(By.ID, 'value')
    element_by_value_index = Element(By.ID, 'value', 0)
    element_by_value_remark = Element(By.ID, 'value', 'this is remark')
    element_by_value_index_timeout = Element(By.ID, 'value', -1, 99)
    element_by_value_index_remark = Element(By.ID, 'value', -1, 'this is remark')
    element_by_value_index_timeout_remark = Element(By.ID, 'value', -1, 99, 'this is remark')

    # dynamic Element
    static_element_by_value = Element()

    def dynamic_element_by_value(self, par) -> Element:
        self.static_element_by_value = (By.ID, f'value_{par}')
        return self.static_element_by_value

    static_element_by_value_index = Element()

    def dynamic_element_by_value_index(self, par) -> Element:
        self.static_element_by_value_index = (By.ID, f'value_{par}', 0)
        return self.static_element_by_value_index

    static_element_by_value_remark = Element()

    def dynamic_element_by_value_remark(self, par) -> Element:
        self.static_element_by_value_remark = (By.ID, f'value_{par}', 'this is remark')
        return self.static_element_by_value_remark

    static_element_by_value_index_timeout = Element()

    def dynamic_element_by_value_index_timeout(self, par) -> Element:
        self.static_element_by_value_index_timeout = (By.ID, f'value_{par}', -1, 99)
        return self.static_element_by_value_index_timeout

    static_element_by_value_index_remark = Element()

    def dynamic_element_by_value_index_remark(self, par) -> Element:
        self.static_element_by_value_index_remark = (By.ID, f'value_{par}', -1, 'this is remark')
        return self.static_element_by_value_index_remark

    static_element_by_value_index_timeout_remark = Element()

    def dynamic_element_by_value_index_timeout_remark(self, par) -> Element:
        self.static_element_by_value_index_timeout_remark = (By.ID, f'value_{par}', -1, 99, 'this is remark')
        return self.static_element_by_value_index_timeout_remark

    # static Elements
    elements_by_value = Elements(By.ID, 'value')
    elements_by_value_timeout = Elements(By.ID, 'value', 99)
    elements_by_value_remark = Elements(By.ID, 'value', 'this is remark')
    elements_by_value_timeout_remark = Elements(By.ID, 'value', 99, 'this is remark')

    # dynamic Element
    static_elements_by_value = Elements()

    def dynamic_elements_by_value(self, par) -> Elements:
        self.static_elements_by_value = (By.ID, f'value_{par}')
        return self.static_elements_by_value

    static_elements_by_value_timeout = Elements()

    def dynamic_elements_by_value_timeout(self, par) -> Elements:
        self.static_elements_by_value_timeout = (By.ID, f'value_{par}', 99)
        return self.static_elements_by_value_timeout

    static_elements_by_value_remark = Elements()

    def dynamic_elements_by_value_remark(self, par) -> Elements:
        self.static_elements_by_value_remark = (By.ID, f'value_{par}', 'this is remark')
        return self.static_elements_by_value_remark

    static_elements_by_value_timeout_remark = Elements()

    def dynamic_elements_by_value_timeout_remark(self, par) -> Elements:
        self.static_elements_by_value_timeout_remark = (By.ID, f'value_{par}', 99, 'this is remark')
        return self.static_elements_by_value_timeout_remark
