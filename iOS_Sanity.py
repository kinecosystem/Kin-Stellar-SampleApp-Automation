from appium import webdriver
import unittest
import time
import requests
import json


class TestCases(unittest.TestCase):
    # vars
    myAddress = ''
    myBalance = ''
    badAddress = ''
    noTrustAddress = 'GANFGTTCZL3D477BSCPR4RMUCX6RLERFUMOKZQYWK22ZFECZ3C7WXIZK'
    qaAccount = 'GBTVB43S7PX2EZKXTHEXAGLVTRBXDOZY2V3LOYN2PSWRIOAFPRMUO2WA'

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

    # TODO: Change lable to label once app gets updated
    # List of tests from <link to test cases>
    def test_1_CreateAccount(self):
        # Verify network buttons exist
        testNetButton = self.driver.find_element_by_accessibility_id('TestNetButton')
        mainNetButton = self.driver.find_element_by_accessibility_id('MainNetButton')

        # Select Testnet
        testNetButton.click()

        # Verify account creation dialog exists
        createAccountDialog = self.driver.find_element_by_name('No Test Net Wallet Yet')
        createWalletLable = self.driver.find_element_by_name('Create a Wallet')
        createWalletLable.click()

        # Account Screen
        # Verify that the address is fine
        address = self.driver.find_element_by_accessibility_id('AddressLable')
        TestCases.myAddress = address.get_attribute('value')
        self.assertEquals(len(TestCases.myAddress), 56)
        self.assertEquals(TestCases.myAddress[0], 'G')

    def test_2_InitialBalanceTest(self):
        # Verify balance labels show up
        balanceHeader = self.driver.find_element_by_accessibility_id('BalanceHeader')
        balanceLabel = self.driver.find_element_by_accessibility_id('BalanceLable')

        # Verify that the balance does not exist
        time.sleep(3)  # Wait for the balance to refresh
        TestCases.myBalance = balanceLabel.get_attribute('value')
        self.assertEquals(TestCases.myBalance, 'Error')

        # Verify on horizon that the account does not exist:
        url = 'https://horizon-testnet.stellar.org/accounts/{}'.format(TestCases.myAddress)
        response = requests.get(url)
        self.assertEquals(response.status_code,404)

    def test_3_DeleteAccount(self):
        # Verify delete button exists
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
        createWalletLable.click()

        # Compare addresses
        newAddress = self.driver.find_element_by_accessibility_id('AddressLable').get_attribute('value')
        self.assertNotEquals(TestCases.myAddress, newAddress)
        TestCases.badAddress = TestCases.myAddress
        TestCases.myAddress = newAddress

    def test_4_Onboarding(self):
        # Verify that the Get Kin button exists
        getKinButton = self.driver.find_element_by_accessibility_id('GetKinButton')
        getKinButton.click()
        time.sleep(20)

        # Verify that you got the Kin
        balanceLabel = self.driver.find_element_by_accessibility_id('BalanceLable')
        self.assertEquals(balanceLabel.get_attribute('value'),'1,000.00 KIN')
        TestCases.myBalance = 1000

        # Verify with horizon
        url = 'https://horizon-testnet.stellar.org/accounts/{}'.format(TestCases.myAddress)
        response = json.loads(requests.get(url).text)
        balances = response['balances']
        self.assertEquals(balances[0]['balance'], '1000.0000000')

    def test_5_KinToEmpty(self):
        # Verify that the send button exists
        sendTransactionButton = self.driver.find_element_by_accessibility_id('SendButton')

        sendTransactionButton.click()

        # Verify that the address and amount fields exists
        addressField = self.driver.find_element_by_accessibility_id('AddressField')
        amountField = self.driver.find_element_by_accessibility_id('AmountField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.badAddress)
        amountField.click()
        amountField.clear()
        amountField.send_keys('350')

        # Verify that the send button exists
        sendButton = self.driver.find_element_by_accessibility_id('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.driver.find_element_by_name('Account not found')
        okButton = self.driver.find_element_by_accessibility_id('OK')
        okButton.click()

    def test_6_KinToNoTrust(self):
        # Verify that the address and amount fields exists
        addressField = self.driver.find_element_by_accessibility_id('AddressField')
        amountField = self.driver.find_element_by_accessibility_id('AmountField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.noTrustAddress)
        amountField.click()
        amountField.clear()
        amountField.send_keys('350')

        # Verify that the send button exists
        sendButton = self.driver.find_element_by_accessibility_id('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.driver.find_element_by_name('No KIN trustline')
        okButton = self.driver.find_element_by_accessibility_id('OK')
        okButton.click()

    def test_7_InsufficientFunds(self):
        # Verify that the address and amount fields exists
        addressField = self.driver.find_element_by_accessibility_id('AddressField')
        amountField = self.driver.find_element_by_accessibility_id('AmountField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.qaAccount)
        amountField.clear()
        amountField.click()
        amountField.send_keys('500000')

        # Verify that the send button exists
        sendButton = self.driver.find_element_by_accessibility_id('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.driver.find_element_by_name('Insufficient funds')
        okButton = self.driver.find_element_by_accessibility_id('OK')
        okButton.click()

    def test_8_GoodTransaction(self):
        # Verify that the address and amount fields exists
        addressField = self.driver.find_element_by_accessibility_id('AddressField')
        amountField = self.driver.find_element_by_accessibility_id('AmountField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.qaAccount)
        amountField.clear()
        amountField.click()
        amountField.send_keys('350')

        # Verify that the send button exists
        sendButton = self.driver.find_element_by_accessibility_id('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.driver.find_element_by_name('Transaction Sent')
        okButton = self.driver.find_element_by_accessibility_id('OK')
        okButton.click()
        self.driver.back()

        # Verify balance changed
        refreshButton = self.driver.find_element_by_name('Refresh')
        refreshButton.click()
        time.sleep(3)
        balanceLabel = self.driver.find_element_by_accessibility_id('BalanceLable')
        self.assertEquals(balanceLabel.get_attribute('value'),'650.00 KIN')



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()
