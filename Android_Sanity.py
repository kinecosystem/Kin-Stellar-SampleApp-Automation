from appium import webdriver
import unittest
import time
import requests
import json
import os

"""
TODO: Wait for sample app to complete in order to actually test
"""
class TestCases(unittest.TestCase):
    # vars
    myAddress = ''
    myBalance = ''
    badAddress = ''
    noTrustAddress = 'GANFGTTCZL3D477BSCPR4RMUCX6RLERFUMOKZQYWK22ZFECZ3C7WXIZK'
    qaAccount = 'GBTVB43S7PX2EZKXTHEXAGLVTRBXDOZY2V3LOYN2PSWRIOAFPRMUO2WA'

    # Desired Capabilities - Change this to whatever you are using
    appPackage = 'kin.sdk.core.sample'
    appActivity = '.ChooseNetworkActivity'
    platformName = 'Android'
    platformVersion = '7.1'
    deviceName = 'Nexus 5X'
    server = 'http://127.0.0.1:4723/wd/hub'

    # Set up Appium and the app
    @classmethod
    def setUpClass(cls):
        # Verify that horizon is up
        if os.system('curl https://horizon-testnet.stellar.org') != 0:
            quit()
        # Sample App should be already installed on the emulator/device

        cls.driver = webdriver.Remote(
            command_executor=TestCases.server,  # Run on local server
            desired_capabilities={
                'appPackage': TestCases.appPackage,
                'appActivity': TestCases.appActivity,
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
        # Clear all data and close the app
        os.system('adb shell pm clear kin.sdk.core.sample')

    def findById(self,id):
        return self.driver.find_element_by_id('kin.sdk.core.sample:id/'+id)

    def findByText(self,text):
        # yes, this is the right syntax
        return self.driver.find_element_by_android_uiautomator('new UiSelector().text("{}")'.format(text))

    # List of tests from <link to test cases>
    def test_1_CreateAccount(self):
        # Verify network buttons exist
        testNetButton = self.findById('btn_test_net')
        mainNetButton = self.findById('btn_main_net')

        # Select Testnet
        testNetButton.click()

        # Verify account creation screen exists
        createWalletButton = self.findById('btn_create_wallet')
        createWalletButton.click()

        # Account Screen
        # TODO: Remove this after the app is fixed
        ok = self.driver.find_element_by_id('android:id/button1')
        ok.click()


        # Verify that the address is fine
        address = self.findById('public_key')
        TestCases.myAddress = address.get_attribute('text')
        self.assertEquals(len(TestCases.myAddress), 56)
        self.assertEquals(TestCases.myAddress[0], 'G')

    def test_2_InitialBalanceTest(self):
        # Verify balance Labels show up
        balanceHeader = self.findByText('getBalance:')
        balanceLabel = self.findById('balance')

        # Verify that the balance does not exist
        time.sleep(3)  # Wait for the balance to refresh
        TestCases.myBalance = balanceLabel.get_attribute('text')
        self.assertEquals(TestCases.myBalance, 'Error')

        # Verify on horizon that the account does not exist:
        url = 'https://horizon-testnet.stellar.org/accounts/{}'.format(TestCases.myAddress)
        response = requests.get(url)
        self.assertEquals(response.status_code,404)

    def test_3_DeleteAccount(self):
        # Verify delete button exists
        deleteAccountButton = self.findById('delete_account_btn')

        deleteAccountButton.click()

        # Verify deletion dialog appears
        okButton = self.driver.find_element_by_id('android:id/button1')

        okButton.click()

        # Verify that you are back on the main screen
        testNetButton = self.findById('btn_test_net')

        testNetButton.click()
        createWalletButton = self.findById('btn_create_wallet')
        createWalletButton.click()

        # Compare addresses
        newAddress = self.findById('public_key').get_attribute('text')
        self.assertNotEquals(TestCases.myAddress, newAddress)
        TestCases.badAddress = TestCases.myAddress
        TestCases.myAddress = newAddress

    def test_4_Onboarding(self):
        # Verify that the Get Kin button exists
        getKinButton = self.findById('get_kin_btn')
        getKinButton.click()
        # Wait enough time for the transaction to go through
        time.sleep(20)

        # Verify that you got the Kin
        balanceLabel = self.findById('balance')
        # TODO: Edit the 1000 KIN when app gets updated
        self.assertEquals(balanceLabel.get_attribute('text'),'1,000.00 KIN')
        TestCases.myBalance = 1000

        # Verify with horizon
        url = 'https://horizon-testnet.stellar.org/accounts/{}'.format(TestCases.myAddress)
        response = json.loads(requests.get(url).text)
        balances = response['balances']
        self.assertEquals(balances[0]['balance'], '1000.0000000')

    def test_5_KinToEmpty(self):
        # Verify that the send button exists
        sendTransactionButton = self.findById('send_transaction_btn')

        sendTransactionButton.click()

        # Verify that the address and amount fields exists
        addressField = self.findById('to_address_input')
        amountField = self.findById('amount_input')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.badAddress)
        amountField.click()
        amountField.clear()
        amountField.send_keys('350')

        # Verify that the send button exists
        sendButton = self.findById('send_transaction_btn')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByText('Account not found')
        okButton = self.driver.find_element_by_id('android:id/button1')
        okButton.click()

    def test_6_KinToNoTrust(self):
        # Verify that the address and amount fields exists
        addressField = self.findById('to_address_input')
        amountField = self.findById('amount_input')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.noTrustAddress)
        amountField.click()
        amountField.clear()
        amountField.send_keys('350')

        # Verify that the send button exists
        sendButton = self.findById('send_transaction_btn')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByText('No KIN trustline')
        okButton = self.driver.find_element_by_id('android:id/button1')
        okButton.click()

    def test_7_InsufficientFunds(self):
        # Verify that the address and amount fields exists
        addressField = self.findById('to_address_input')
        amountField = self.findById('amount_input')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.qaAccount)
        amountField.clear()
        amountField.click()
        amountField.send_keys('500000')

        # Verify that the send button exists
        sendButton = self.findById('send_transaction_btn')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByText('Insufficient funds')
        okButton = self.driver.find_element_by_id('android:id/button1')
        okButton.click()

    def test_8_GoodTransaction(self):
        # Verify that the address and amount fields exists
        addressField = self.findById('to_address_input')
        amountField = self.findById('amount_input')

        addressField.click()
        addressField.clear()
        addressField.send_keys(TestCases.qaAccount)
        amountField.clear()
        amountField.click()
        amountField.send_keys('350')

        # Verify that the send button exists
        sendButton = self.findById('send_transaction_btn')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByText('Transaction Sent')
        okButton = self.driver.find_element_by_id('android:id/button1')
        okButton.click()
        self.driver.back()

        # Verify balance changed
        refreshButton = self.findById('refresh_btn')
        refreshButton.click()
        time.sleep(3)
        balanceLabel = self.findById('balance')
        # TODO: update 650 kin when app works
        self.assertEquals(balanceLabel.get_attribute('text'),'650.00 KIN')



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()
