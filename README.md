# Kin-Stellar-SampleApp-Automation

**Work in progress**
A repository for the QA automation tests for the Kin Stellar SDK sample apps
[iOS](https://github.com/kinfoundation/kin-sdk-core-stellar-ios) / [Android](https://github.com/kinfoundation/kin-sdk-core-stellar-android)

# Warning
**After running these tests, all wallets on the sample app will be deleted, and you will lose access to them.**

## Usage
**The app should already be installed on the emulator/simulator prior to running the test, and no test-net wallets should be on it.**

1. Open a new Appium server
2. For android,turn on your emulator.
3. Configure your desired capabilities inside the relevant sanity file
2. Open your terminal in the folder of this project
3. Run the command
```
pytest -v -x --no-print-logs iOS/Android_Sanity.py
```

## Prerequisites

Developed on Python  3.6

Python dependencies:
```
pip3 install Appium-Python-Client requests pytest
pip3 install git+https://github.com/kinecosystem/kin-core-python
```
In addition to these python packages, this following steps are needed:
* Install Appium - [Download](https://github.com/appium/appium-desktop/releases/tag/v1.3.1)
* For Android, install Android Studio - [Download](https://developer.android.com/studio/index.html)
* For iOS, install Xcode - [Download](https://itunes.apple.com/ao/app/xcode/id497799835?mt=12)
* For iOS, install the following brew package:
```
brew install carthage
```

# Example

[![iOS Sanity](https://i.imgur.com/IMgzltX.jpg)](https://www.youtube.com/watch?v=wPzNuMOAea8 "iOS Sanity")

