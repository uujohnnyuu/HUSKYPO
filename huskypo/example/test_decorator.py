from huskypo.example.my_page import MyPage


class TestDecorator:

    def test_decorator_dynamic_element_attributes():

        driver = 'DRIVER'
        my_page = MyPage(driver)

        my_page.d_element('123456').test_attributes()
        my_page.d_elements('777777').test_attributes()
