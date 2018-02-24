from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
import sys
from web3 import Web3, HTTPProvider
import json

from accounts.models import EthAccount, Transaction


class Command(BaseCommand):
    help = 'Transfer UTCoin.'

    def add_arguments(self, parser):
        parser.add_argument('from', type=str, help='From user name')
        parser.add_argument('to', type=str, help='To user name')
        parser.add_argument('amount', type=float, help='Amount (min: 0.001 UTC)')

    def handle(self, *args, **options):
        # Load contract
        web3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
        abi = self.load_abi(settings.ARTIFACT_PATH)
        UTCoin = web3.eth.contract(abi=abi, address=settings.UTCOIN_ADDRESS)

        # Load decimals
        decimals = UTCoin.call().decimals()
        num_suffix = 10 ** decimals

        # Receive params
        from_username = options['from']
        to_username = options['to']
        amount = options['amount']
        amount_int = int(amount * num_suffix)

        from_user = User.objects.filter(username=from_username).first()
        if not from_user:
            print(f'ユーザ名 @{from_username} は存在しません。')
            sys.exit(1)

        to_user = User.objects.filter(username=to_username).first()
        if not to_user:
            print(f'ユーザ名 @{to_username} は存在しません。')
            sys.exit(1)

        from_account = EthAccount.objects.get(user=from_user)
        from_address = from_account.address

        to_account = EthAccount.objects.get(user=to_user)
        to_address = to_account.address

        # Get balances
        from_balance = UTCoin.call().balanceOf(from_address)
        to_balance = UTCoin.call().balanceOf(to_address)
        from_balance_fixed = from_balance / num_suffix
        to_balance_fixed = to_balance / num_suffix
        from_eth_balance = web3.fromWei(web3.eth.getBalance(from_address), 'ether')
        to_eth_balance = web3.fromWei(web3.eth.getBalance(to_address), 'ether')

        print('\n-----------------------------------------------------')
        print('FROM')
        print(f'#{from_user.id} @{from_username}:')
        print(f'  address: {from_address}')
        print(f'  UTCoin balance: {from_balance_fixed} UTC')
        print(f'  ETH balance: {from_eth_balance} ETH')

        print('\nTO')
        print(f'#{to_user.id} @{to_username}:')
        print(f'  address: {to_address}')
        print(f'  UTCoin balance: {to_balance_fixed} UTC')
        print(f'  ETH balance: {to_eth_balance} ETH')
        print('-----------------------------------------------------\n')

        # Confirm
        print(f'@{from_username} [{amount} UTC] ---> @{to_username}\n')
        confirm = input('本当に送金しますか？(y/N): ')
        if confirm != 'y':
            print('キャンセルしました。')
            sys.exit(0)
        print('Please wait...')

        # Transfer UTCoin
        if web3.personal.unlockAccount(from_address, from_account.password, duration=hex(300)):
            try:
                tx_hash = UTCoin.transact({'from': from_address}).transfer(to_address, amount_int)

                # Create Transaction
                transaction_info = web3.eth.getTransaction(tx_hash)
                transaction = Transaction.objects.create(
                    user=from_user,
                    eth_account=from_account,
                    tx_hash=tx_hash,
                    from_address=from_address,
                    to_address=to_address,
                    amount=amount_int,
                    gas=transaction_info['gas'],
                    gas_price=transaction_info['gasPrice'],
                    value=transaction_info['value'],
                    network_id=1
                )
            except Exception as e:
                print(e)
                print('トランザクションに失敗しました。')
                sys.exit(1)
        else:
            print('アカウントのアンロックに失敗しました。')
            sys.exit(1)

        print('送金が完了しました！')

    @staticmethod
    def load_abi(file_path):
        artifact = open(file_path, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        return abi
