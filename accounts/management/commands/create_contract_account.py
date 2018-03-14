from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import sys
from web3 import Web3, HTTPProvider
import secrets
import string
import qrcode

from accounts.models import Contract


class Command(BaseCommand):
    help = 'Create Ethereum account for the contract.'

    def add_arguments(self, parser):
        parser.add_argument('contract_id', type=int, help='contract object ID')

    def handle(self, *args, **options):
        contract_id = options['contract_id']

        contract = Contract.objects.filter(pk=contract_id).first()
        if not contract:
            print(f'指定された ID のコントラクトは見つかりませんでした。')
            sys.exit(1)

        print('\n-----------------------------------------')
        print('ID:', contract.id)
        print('User:', contract.user)
        print('address:', contract.address)
        print('password:', contract.password)
        print('qrcode:', contract.qrcode)
        print('name:', contract.name)
        print('is_active:', contract.is_active)
        print('is_verified:', contract.is_verified)
        print('is_banned:', contract.is_banned)
        print('verified_at:', contract.verified_at)
        print('created_at:', contract.created_at)
        print('modified_at:', contract.modified_at)
        print('-----------------------------------------\n')

        if contract.address:
            print('既に Ethereum アカウントが作成されています。')
            sys.exit(1)

        # 確認
        confirm = input('Ethereum アカウントを作成しますか？(y/N): ')
        if confirm != 'y':
            print('キャンセルしました。')
            sys.exit(0)

        # Ethereum アカウント作成
        try:
            with transaction.atomic():
                # Generate random password and address
                web3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for _ in range(30))
                address = web3.personal.newAccount(password)

                # Generate QR code
                img = qrcode.make(address)
                file_name = address + '.png'
                file_path = '/images/qrcode/contract/' + file_name
                img.save(settings.MEDIA_ROOT + file_path)

                # Save contract object
                contract.address = address
                contract.password = password
                contract.qrcode = file_path
                contract.modified_at = timezone.now()
                contract.save()
        except Exception as e:
            print('\nError:')
            print(e)
            print('\nEthereum アカウントの作成に失敗しました。')
            sys.exit(1)

        print('\nEthereum アカウントを作成しました！')
        print('Address:', contract.address)
        print('Password:', contract.password)
        print('QR code:', contract.qrcode)

        print('\n認証を行うには次のコマンドを実行してください:')
        print(f'  > python manage.py verify_contract {contract_id}')
