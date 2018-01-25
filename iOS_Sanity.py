from appium import webdriver
import unittest

class TestCases(unittest.TestCase):

    # Set up Appium and the app
    def setUp(self):
        # Sample App should be already installed on the emulator # TODO: add option to install
        bundleId = 'com.kinfoundation.KinSampleApp'
        self.driver = webdriver.Remote(
            command_executor = 'http://127.0.0.1:4723/wd/hub', # Run on local server
            desired_capabilities = {
                'bundleId': bundleId,
                'platformName': 'iOS',
                'platformVersion': '11.2',
                'deviceName': 'iPhone 7'  # TODO: name and version from somewhere else
            }
        )
        self._values = []

    # Gets the test run is over
    def tearDown(self):
        self.driver.quit()

    # List of tests from <link to test cases>
    def test_mainScreen(self):
        testNetButton = self.driver.find_element_by_accessibility_id('TestNetButton')
        mainNetButton = self.driver.find_element_by_accessibility_id('MainNetButton')

        self.assertIsNotNone(testNetButton)
        self.assertIsNotNone(mainNetButton)

    def test_failthis(self):
        # This should fail
        testNetButton = self.driver.find_element_by_accessibility_id('TestNetButton')
        self.assertIsNone(testNetButton)



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()