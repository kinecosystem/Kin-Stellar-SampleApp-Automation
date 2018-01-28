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
            command_executor='http://127.0.0.1:4723/wd/hub',  # Run on local server
            desired_capabilities={
                'bundleId': bundleId,
                'platformName': 'iOS',
                'platformVersion': '11.2',
                'deviceName': 'iPhone 7'  # TODO: name and version from somewhere else
            }
        )
        cls._values = []
        # Timeout for element searching
        # Official documentation says its in millisecond, but it actually works in seconds for me
        cls.driver.implicitly_wait(10)

    # Called when the test run is over
    @classmethod
    def tearDownClass(cls):
        # Re-open the app
        cls.driver.reset()
        # Enter the testnet account screen
        testNetButton = cls.driver.find_element_by_accessibility_id('TestNetButton')
        testNetButton.click()
        # Delete your account
        deleteAccountButton = cls.driver.find_element_by_accessibility_id('DeleteButton')
        deleteAccountButton.click()
        okButton = cls.driver.find_element_by_accessibility_id('OK')
        okButton.click()
        time.sleep(3)
        cls.driver.quit()

    # List of tests from <link to test cases>
    def test_1_CreateAccount(self):
        testNetButton = self.driver.find_element_by_accessibility_id('TestNetButton')
        mainNetButton = self.driver.find_element_by_accessibility_id('MainNetButton')

        # Verify network buttons exist
        self.assertIsNotNone(testNetButton)
        self.assertIsNotNone(mainNetButton)

        # Select Testnet
        testNetButton.click()

        # Verify account creation dialog shows up
        createAccountDialog = self.driver.find_element_by_name('No Test Net Wallet Yet')
        createWalletLable = self.driver.find_element_by_name('Create a Wallet')
        self.assertIsNotNone(createAccountDialog)
        createWalletLable.click()

        # Account Screen
        # Verify that the address is fine
        address = self.driver.find_element_by_accessibility_id('AddressLable')
        self.assertIsNotNone(address)
        self.assertEquals(len(address.get_attribute('value')), 56)
        self.assertEquals(address.get_attribute('value')[0], 'G')

    def test_2_InitialBalanceTest(self):
        balanceHeader = self.driver.find_element_by_accessibility_id('BalanceHeader')
        balanceLabel = self.driver.find_element_by_accessibility_id('BalanceLable')

        # Verify balance labels show up
        self.assertIsNotNone(balanceHeader)
        self.assertIsNotNone(balanceLabel)

        # Verify that the balance does not exist
        self.assertEquals(balanceLabel.get_attribute('value'), 'Error')
        # TODO verify with horizon

    def test_3_DeleteAccount(self):
        # Remember your address
        oldAddress = self.driver.find_element_by_accessibility_id('AddressLable').get_attribute('value')

        # Verify delete button shows up
        deleteAccountButton = self.driver.find_element_by_accessibility_id('DeleteButton')

        deleteAccountButton.click()

        # Verify deletion dialog appears
        okButton = self.driver.find_element_by_accessibility_id('OK')

        okButton.click()

        # Verify that you are back on the main screen
        testNetButton = self.driver.find_element_by_accessibility_id('TestNetButton')

        testNetButton.click()
        createAccountDialog = self.driver.find_element_by_name('No Test Net Wallet Yet')
        createWalletLable = self.driver.find_element_by_name('Create a Wallet')
        self.assertIsNotNone(createAccountDialog)
        createWalletLable.click()

        # Compare addresses
        newAddress = self.driver.find_element_by_accessibility_id('AddressLable').get_attribute('value')
        self.assertNotEquals(oldAddress, newAddress)


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()
