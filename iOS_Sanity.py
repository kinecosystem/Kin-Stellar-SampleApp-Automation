from appium import webdriver
import unittest
import time
import requests
import json
import os


class TestCases(unittest.TestCase):
    # vars
    myAddress = ''
    badAddress = ''
    noTrustAddress = 'GANFGTTCZL3D477BSCPR4RMUCX6RLERFUMOKZQYWK22ZFECZ3C7WXIZK'
    qaAccount = 'GBDUPSZP4APH3PNFIMYMTHIGCQQ2GKTPRBDTPCORALYRYJZJ35O2LOBL'

    # Desired Capabilities:
    bundleId = 'com.kinfoundation.KinSampleApp'
    platformName = 'iOS'
    platformVersion = '11.2'
    deviceName = 'iPhone 8 Plus'
    server = 'http://127.0.0.1:4723/wd/hub'

    # Set up Appium and the app
    @classmethod
    def setUpClass(cls):
        # Verify that horizon is up
        if os.system('curl https://horizon-testnet.stellar.org') != 0:
            quit()
        # Sample App should be already installed on the emulator
        cls.driver = webdriver.Remote(
            command_executor= TestCases.server,  # Run on local server
            desired_capabilities={
                'bundleId': TestCases.bundleId,
                'platformName': TestCases.platformName,
                'platformVersion': TestCases.platformVersion,
                'deviceName': TestCases.deviceName
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

    def findById(self,id):
        return self.driver.find_element_by_accessibility_id(id)

    def findByName(self,name):
        return self.driver.find_element_by_name(name)

    # List of tests from <https://goo.gl/eBREhe>
    def test_1_CreateAccount(self):
        # Verify network buttons exist
        testNetButton = self.findById('TestNetButton')
        mainNetButton = self.findById('MainNetButton')

        # Select Testnet
        testNetButton.click()

        # Verify account creation dialog exists
        createAccountDialog = self.findByName('No Test Net Wallet Yet')
        createWalletLabel = self.findByName('Create a Wallet')
        createWalletLabel.click()

        # Account Screen
        # Verify that the address is fine
        address = self.findById('AddressLabel')
        TestCases.myAddress = address.get_attribute('value')
        self.assertEquals(len(TestCases.myAddress), 56)
        self.assertEquals(TestCases.myAddress[0], 'G')

    def test_2_InitialBalanceTest(self):
        # Verify balance Labels show up
        balanceHeader = self.findById('BalanceHeader')
        balanceLabel = self.findById('BalanceLabel')

        # Verify that the balance does not exist
        time.sleep(3)  # Wait for the balance to refresh
        myBalance = balanceLabel.get_attribute('value')
        self.assertEquals(myBalance, 'Error')

        # Verify on horizon that the account does not exist:
        url = 'https://horizon-testnet.stellar.org/accounts/{}'.format(TestCases.myAddress)
        response = requests.get(url)
        self.assertEquals(response.status_code,404)

    def test_3_DeleteAccount(self):
        # Verify delete button exists
        deleteAccountButton = self.findById('DeleteButton')

        deleteAccountButton.click()

        # Verify deletion dialog appears
        okButton = self.findById('OK')

        okButton.click()

        # Verify that you are back on the main screen
        testNetButton = self.findById('TestNetButton')

        testNetButton.click()
        createAccountDialog = self.findByName('No Test Net Wallet Yet')
        createWalletLabel = self.findByName('Create a Wallet')
        createWalletLabel.click()

        # Compare addresses
        newAddress = self.findById('AddressLabel').get_attribute('value')
        self.assertNotEquals(TestCases.myAddress, newAddress)
        TestCases.badAddress = TestCases.myAddress
        TestCases.myAddress = newAddress

    def test_4_Onboarding(self):
        # Verify that the Get Kin button exists
        getKinButton = self.findById('GetKinButton')
        getKinButton.click()
        time.sleep(20)

        # Verify that you got the Kin
        balanceLabel = self.findById('BalanceLabel')
        self.assertEquals(balanceLabel.get_attribute('value'),'6,000.00 KIN')

        # Verify with horizon
        url = 'https://horizon-testnet.stellar.org/accounts/{}'.format(TestCases.myAddress)
        response = json.loads(requests.get(url).text)
        balances = response['balances']
        self.assertEquals(balances[0]['balance'], '6000.0000000')

    def test_5_KinToEmpty(self):
        # Verify that the send button exists
        sendTransactionButton = self.findById('SendButton')

        sendTransactionButton.click()

        # Verify that the address and amount fields exists
        addressField = self.findById('AddressField')
        amountField = self.findById('AmountField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.badAddress)
        amountField.click()
        amountField.clear()
        amountField.send_keys('350')

        # Verify that the send button exists
        sendButton = self.findById('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByName('Payment failed')
        okButton = self.findById('OK')
        okButton.click()

    def test_6_KinToNoTrust(self):
        # Verify that the address and amount fields exists
        addressField = self.findById('AddressField')
        amountField = self.findById('AmountField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.noTrustAddress)
        amountField.click()
        amountField.clear()
        amountField.send_keys('350')

        # Verify that the send button exists
        sendButton = self.findById('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByName('Payment failed')
        okButton = self.findById('OK')
        okButton.click()

    def test_7_InsufficientFunds(self):
        # Verify that the address and amount fields exists
        addressField = self.findById('AddressField')
        amountField = self.findById('AmountField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.qaAccount)
        amountField.click()
        amountField.clear()
        amountField.send_keys('500000')

        # Verify that the send button exists
        sendButton = self.findById('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByName('Payment failed')
        okButton = self.findById('OK')
        okButton.click()

    def test_8_LongMemo(self):
        # Verify that the address and amount fields exists
        addressField = self.findById('AddressField')
        amountField = self.findById('AmountField')
        memoField = self.findById('MemoField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.qaAccount)
        amountField.click()
        amountField.clear()
        amountField.send_keys('350')
        memoField.click()
        memoField.clear()

        # Memo should be restricted to 32 characters
        memoField.send_keys('a'*50)

        # Verify that the send button exists
        sendButton = self.findById('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByName('Error')
        okButton = self.findById('OK')
        okButton.click()

    def test_9_GoodTransaction(self):
        # Verify that the address and amount fields exists
        addressField = self.findById('AddressField')
        amountField = self.findById('AmountField')
        memoField = self.findById('MemoField')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.qaAccount)
        amountField.click()
        amountField.clear()
        amountField.send_keys('350')
        memoField.click()
        memoField.clear()
        memoField.send_keys('Hello stellar')

        # Verify that the send button exists
        sendButton = self.findById('SendButton')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByName('Transaction Sent')
        okButton = self.findById('OK')
        okButton.click()
        self.driver.back()

        # Verify balance changed
        time.sleep(3)
        balanceLabel = self.findById('BalanceLabel')
        self.assertEquals(balanceLabel.get_attribute('value'),'5,650.00 KIN')

    # Since this would be test_10 it would start before test_1_
    # Its the last test, so I will leave it like that
    def test_9a_RecentHistory(self):

        # This page is dynamically generated, so we need to search elements with labels

        recentButton = self.findById('RecentButton')
        recentButton.click()
        firstTX = self.findByName('6000')
        latestTX = self.findByName('350')



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()
