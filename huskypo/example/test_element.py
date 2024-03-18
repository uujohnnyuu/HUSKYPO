from huskypo.example.my_page import MyPage


class TestElement:

    def test_element_attributes():

        driver = 'DRIVER'
        my_page = MyPage(driver)

        # static Element
        my_page.element_by_value.find()
        my_page.element_by_value.test_attributes()
        my_page.element_by_value_index.test_attributes()
        my_page.element_by_value_remark.test_attributes()
        my_page.element_by_value_index_timeout.test_attributes()
        my_page.element_by_value_index_remark.test_attributes()
        my_page.element_by_value_index_timeout_remark.test_attributes()

        # Static elements with empty descriptor
        my_page.static_element_by_value.test_attributes()
        my_page.static_element_by_value_index.test_attributes()
        my_page.static_element_by_value_remark.test_attributes()
        my_page.static_element_by_value_index_timeout.test_attributes()
        my_page.static_element_by_value_index_remark.test_attributes()
        my_page.static_element_by_value_index_timeout_remark.test_attributes()

        # Assigning attribute to empty descriptor -> dynamic element
        my_page.dynamic_element_by_value('par1').test_attributes()
        my_page.dynamic_element_by_value_index('par1').test_attributes()
        my_page.dynamic_element_by_value_remark('par1').test_attributes()
        my_page.dynamic_element_by_value_index_timeout('par1').test_attributes()
        my_page.dynamic_element_by_value_index_remark('par1').test_attributes()
        my_page.dynamic_element_by_value_index_timeout_remark('par1').test_attributes()

        # Using static element after assigning
        my_page.static_element_by_value.test_attributes()
        my_page.static_element_by_value_index.test_attributes()
        my_page.static_element_by_value_remark.test_attributes()
        my_page.static_element_by_value_index_timeout.test_attributes()
        my_page.static_element_by_value_index_remark.test_attributes()
        my_page.static_element_by_value_index_timeout_remark.test_attributes()
