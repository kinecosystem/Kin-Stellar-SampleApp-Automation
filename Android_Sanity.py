from appium import webdriver
import unittest
import time
import requests
import json
import os
from account_creator import create_activated_account, create_no_trust_account 

"""
TODO: Wait for sample app to complete in order to actually test
"""
class TestCases(unittest.TestCase):
    # vars
    myAddress = ''
    badAddress = ''
    noTrustAddress = ''
    qaAccount = ''
    sdk_package_name = 'kin.core.sample'
    kin_test_blockchain_url = 'https://horizon-playground.kininfrastructure.com'

    # Desired Capabilities - Change this to whatever you are using
    appPackage = 'kin.core.sample'
    appActivity = '.ChooseNetworkActivity'
    platformName = 'Android'
    platformVersion = '8.0.0'
    deviceName = 'emulator-5554'
    server = 'http://127.0.0.1:4723/wd/hub'

    # Set up Appium and the app
    @classmethod
    def setUpClass(cls):
        # Verify that horizon is up
        if os.system('curl ' + TestCases.kin_test_blockchain_url) != 0:
            quit()
        
        TestCases.noTrustAddress = create_no_trust_account()   
        TestCases.qaAccount = create_activated_account() 
        # Sample App should be already installed on the emulator/device
        os.system('adb shell pm clear ' + TestCases.sdk_package_name)

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
        os.system('adb shell pm clear ' + TestCases.sdk_package_name)

    def findById(self,id):
        return self.driver.find_element_by_id(TestCases.sdk_package_name + ':id/'+id)

    def findByText(self,text):
        # yes, this is the right syntax
        return self.driver.find_element_by_android_uiautomator('new UiSelector().text("{}")'.format(text))

    # List of tests from <https://goo.gl/eBREhe>
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
        # Verify that the address is fine
        address = self.findById('public_key')
        TestCases.myAddress = address.get_attribute('text')
        self.assertEquals(len(TestCases.myAddress), 56)
        self.assertEquals(TestCases.myAddress[0], 'G')

    def test_2_InitialBalanceTest(self):
        # Verify balance Labels show up
        balanceHeader = self.findByText('getBalance:')
        balanceLabel = self.findById('balance')
        statusLable = self.findById('status')

        # Verify that the balance does not exist
        time.sleep(3)  # Wait for the balance to refresh
        myBalance = balanceLabel.get_attribute('text')
        self.assertEquals(myBalance, 'Error')
        myStatus = statusLable.get_attribute('text')
        self.assertEquals(myStatus, 'Not Created')


        # Verify on horizon that the account does not exist:
        url = '{}/accounts/{}'.format(TestCases.kin_test_blockchain_url, TestCases.myAddress)
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
        getKinButton = self.findById('onboard_btn')
        getKinButton.click()
        # Wait enough time for the transaction to go through
        time.sleep(20)

        # Verify that you got the Kin
        balanceLabel = self.findById('balance')
        self.assertEquals(balanceLabel.get_attribute('text'),'6000.0000000')

        # Verify account status changed
        self.findByText('Activated')

        # Verify with horizon
        url = '{}/accounts/{}'.format(TestCases.kin_test_blockchain_url, TestCases.myAddress)
        response = json.loads(requests.get(url).text)
        balances = response['balances']
        self.assertEquals(balances[0]['balance'], '6000.0000000')

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
        self.driver.hide_keyboard()
        sendButton = self.findById('send_transaction_btn')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByText('Account {} was not found'.format(TestCases.badAddress))
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
        self.driver.hide_keyboard()
        sendButton = self.findById('send_transaction_btn')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByText('Account {} is not activated'.format(TestCases.noTrustAddress))
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
        self.driver.hide_keyboard()
        sendButton = self.findById('send_transaction_btn')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.findByText('Not enough kin to perform the transaction.')
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
        self.driver.hide_keyboard()
        sendButton = self.findById('send_transaction_btn')
        sendButton.click()

        # Verify that the transaction failed
        errorDialog = self.driver.find_element_by_android_uiautomator\
            ('new UiSelector().textContains("Transaction id")')
        okButton = self.driver.find_element_by_id('android:id/button1')
        okButton.click()
        self.driver.find_element_by_accessibility_id('Navigate up').click() # Back button

        # Verify balance changed
        refreshButton = self.findById('refresh_btn')
        refreshButton.click()
        time.sleep(3)
        balanceLabel = self.findById('balance')
        self.assertEquals(balanceLabel.get_attribute('text'),'5650.0000000')



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    main()
