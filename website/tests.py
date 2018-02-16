from django.test import TestCase
from django.conf import settings
from web3 import Web3, HTTPProvider
import json

class TestTotalSupply(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestTotalSupply, self).__init__(*args, **kwargs)
        web3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
        coinbase = web3.eth.coinbase

        # Parse artifact
        artifact = open(settings.ARTIFACT_PATH, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        bytecode = json_dict['bytecode']

        # Deploy contract
        UTCoin = web3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = UTCoin.deploy(transaction={'from': coinbase})
        UTCoin.address = web3.eth.getTransactionReceipt(tx_hash)['contractAddress']

        self.coinbase = coinbase
        self.UTCoin = UTCoin

    def test_get_total_supply(self):
        self.assertEqual(self.UTCoin.call().totalSupply(), 1000000000) # 1,000,000 UTC

class TestBalanceOf(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestBalanceOf, self).__init__(*args, **kwargs)
        web3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
        accounts = web3.eth.accounts

        # Parse artifact
        artifact = open(settings.ARTIFACT_PATH, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        bytecode = json_dict['bytecode']

        # Deploy contract
        UTCoin = web3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = UTCoin.deploy(transaction={'from': accounts[0]})
        UTCoin.address = web3.eth.getTransactionReceipt(tx_hash)['contractAddress']

        self.accounts = accounts
        self.UTCoin = UTCoin

    def test_balance_of(self):
        total_supply = self.UTCoin.call().totalSupply()
        self.assertEqual(self.UTCoin.call().balanceOf(self.accounts[0]), total_supply) # 1,000,000 UTC
        self.assertEqual(self.UTCoin.call().balanceOf(self.accounts[1]), 0) # 0 UTC

class TestTransfer(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestTransfer, self).__init__(*args, **kwargs)
        web3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
        accounts = web3.eth.accounts

        # Parse artifact
        artifact = open(settings.ARTIFACT_PATH, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        bytecode = json_dict['bytecode']

        # Deploy contract
        UTCoin = web3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = UTCoin.deploy(transaction={'from': accounts[0]})
        UTCoin.address = web3.eth.getTransactionReceipt(tx_hash)['contractAddress']

        self.accounts = accounts
        self.UTCoin = UTCoin

    def test_transfer(self):
        from_address = self.accounts[0]
        to_address = self.accounts[1]

        from_starting_balance = self.UTCoin.call().balanceOf(from_address)
        to_starting_balance = self.UTCoin.call().balanceOf(to_address)
        from_ending_balance = 0
        to_ending_balance = 0

        num_suffix = 1000
        amount = int(10.123 * num_suffix)

        tx_hash = self.UTCoin.transact({'from': from_address}).transfer(to_address, amount)

        self.assertEqual(self.UTCoin.call().balanceOf(from_address), from_starting_balance - amount) # 999,989.877 UTC
        self.assertEqual(self.UTCoin.call().balanceOf(to_address), to_starting_balance + amount) # 10.123 UTC
