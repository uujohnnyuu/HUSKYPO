from huskypo.example.my_page import MyPage


class TestMyTest:

    def test_element_attributes():

        driver = 'DRIVER'
        my_page = MyPage(driver)

        my_page.element_by_value.test_attributes()
        my_page.element_by_value_index.test_attributes()
        my_page.element_by_value_remark.test_attributes()
        my_page.element_by_value_index_timeout.test_attributes()
        my_page.element_by_value_index_remark.test_attributes()
        my_page.element_by_value_index_timeout_remark.test_attributes()

        my_page.elements_by_value.test_attributes()
        my_page.elements_by_value_timeout.test_attributes()
        my_page.elements_by_value_remark.test_attributes()
        my_page.elements_by_value_timeout_remark.test_attributes()

        my_page.d_element(123).test_attributes()
        my_page.d_elements(123456).test_attributes()

        my_page.dynamic_element(123).test_attributes()
        my_page.static_element.test_attributes()

        my_page.dynamic_elements(123456).test_attributes()
        my_page.static_elements.test_attributes()
