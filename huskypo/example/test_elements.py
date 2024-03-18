from huskypo.example.my_page import MyPage


class TestElements:

    def test_elements_attributes():

        driver = 'DRIVER'
        my_page = MyPage(driver)

        # static Elements
        my_page.elements_by_value.test_attributes()
        my_page.elements_by_value_timeout.test_attributes()
        my_page.elements_by_value_remark.test_attributes()
        my_page.elements_by_value_timeout_remark.test_attributes()

        # Static elements with empty descriptor
        my_page.static_elements_by_value.test_attributes()
        my_page.static_elements_by_value_timeout.test_attributes()
        my_page.static_elements_by_value_remark.test_attributes()
        my_page.static_elements_by_value_timeout_remark.test_attributes()

        # Assigning attribute to empty descriptor -> dynamic elements
        my_page.dynamic_elements_by_value('par1').test_attributes()
        my_page.dynamic_elements_by_value_timeout('par1').test_attributes()
        my_page.dynamic_elements_by_value_remark('par1').test_attributes()
        my_page.dynamic_elements_by_value_timeout_remark('par1').test_attributes()

        # Using static elements after assigning
        my_page.static_elements_by_value.test_attributes()
        my_page.static_elements_by_value_timeout.test_attributes()
        my_page.static_elements_by_value_remark.test_attributes()
        my_page.static_elements_by_value_timeout_remark.test_attributes()
