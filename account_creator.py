import time
import os
from functools import wraps
import kin
import requests
from kin.sdk import Keypair
import stellar_base
from stellar_base.network import NETWORKS

kin_test_blockchain_url = 'https://horizon-playground.kininfrastructure.com'
kin_test_blockchain_id = 'Kin Playground Network ; June 2018'
kin_test_blockchain_issuer_id = 'GBC3SG6NGTSZ2OMH3FFGB7UVRQWILW367U4GSOOF4TFSZONV42UJXUH7'
kin_faucet = 'http://friendbot-playground.kininfrastructure.com'
kin_friend_bot = 'http://faucet-playground.kininfrastructure.com'
amount = 1000

def trust_kin(private_seed):
    NETWORKS['CUSTOM'] = kin_test_blockchain_id
    kin_sdk = kin.SDK(
        secret_key=private_seed,
        horizon_endpoint_uri=kin_test_blockchain_url,
        network='CUSTOM',
        kin_asset=kin.Asset.native())
    kin_asset = stellar_base.asset.Asset(
        "KIN", kin_test_blockchain_issuer_id)
    kin_sdk._trust_asset(kin_asset)

def fund_lumens(public_address):
    res = requests.get(kin_faucet,
                        params={'addr': public_address})
    res.raise_for_status()
    return res.json()

def fund_kin(public_address):
    res = requests.get(kin_friend_bot + '/fund',
                        params={'account': public_address,
                                'amount': amount})
    res.raise_for_status()
    return res.json()

def create_activated_account():
    # generates a file that can be 'sourced' and creates environment vars for
    # payment-service
    keys = Keypair.random()
    public_address = keys.address().decode()
    private_seed = keys.seed().decode()

    print('# creating %s' % public_address)
    fund_lumens(public_address)
    trust_kin(private_seed)
    fund_kin(public_address)
    return public_address

def create_no_trust_account():
    # generates a file that can be 'sourced' and creates environment vars for
    # payment-service
    keys = Keypair.random()
    public_address = keys.address().decode()
    private_seed = keys.seed().decode()

    print('# creating %s' % public_address)
    fund_lumens(public_address)
    return public_address
