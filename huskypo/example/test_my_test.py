from huskypo.example.my_page import MyPage


class TestMyTest:

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
