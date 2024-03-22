from huskypo import logconfig, Timeout
from huskypo.example.test_my_test import TestMyTest

if __name__ == '__main__':

    logconfig.basic()

    # Modify default timeout from 30 to 60
    Timeout.DEFAULT = 60
    TestMyTest.test_element_attributes()
