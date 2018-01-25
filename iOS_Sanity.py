from appium import webdriver
import unittest
import time

class TestCases(unittest.TestCase):

    # Set up Appium and the app
    @classmethod
    def setUpClass(cls):
        # Sample App should be already installed on the emulator # TODO: add option to install
        bundleId = 'com.kinfoundation.KinSampleApp'
        cls.driver = webdriver.Remote(
            command_executor = 'http://127.0.0.1:4723/wd/hub', # Run on local server
            desired_capabilities = {
                'bundleId': bundleId,
                'platformName': 'iOS',
                'platformVersion': '11.2',
                'deviceName': 'iPhone 7'  # TODO: name and version from somewhere else
            }
        )
        cls._values = []

    # Called when the test run is over
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # List of tests from <link to test cases>
    def test_1_CreateAccount(self):
        testNetButton = self.driver.find_element_by_accessibility_id('TestNetButton')
        mainNetButton = self.driver.find_element_by_accessibility_id('MainNetButton')
        createAccountDialog = self.driver.find_element_by_name('No Test Net Wallet Yet')
        createWalletLable = self.driver.find_element_by_name('Create a Wallet')
        address = self.driver.find_element_by_accessibility_id('AddressLable')

        # Verify network buttons exist
        self.assertIsNotNone(testNetButton)
        self.assertIsNotNone(mainNetButton)

        # Select Testnet
        testNetButton.click()

        # Verify account creation dialog shows up
        self.assertIsNotNone(createAccountDialog)
        createWalletLable.click()

        # Account Screen
        # Verify that the address is fine
        self.assertIsNotNone(address)
        self.assertEquals(len(address.get_attribute('value')),56)
        self.assertEquals(address.get_attribute('value')[0],'G')


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()