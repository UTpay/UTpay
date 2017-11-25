from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import sys
from web3 import Web3, HTTPProvider
import secrets
import string
import qrcode

from accounts.models import Api

class Command(BaseCommand):
    help = 'Create Ethereum account for user defined API.'

    def add_arguments(self, parser):
        parser.add_argument('api_id', type=int, help='API object ID')

    def handle(self, *args, **options):
        api_id = options['api_id']

        api = Api.objects.filter(pk=api_id).first()
        if not api:
            print(f'指定された ID の API は見つかりませんでした。')
            sys.exit(1)

        print('\n-----------------------------------------')
        print('ID:', api.id)
        print('User:', api.user)
        print('address:', api.address)
        print('password:', api.password)
        print('qrcode:', api.qrcode)
        print('name:', api.name)
        print('is_active:', api.is_active)
        print('is_verified:', api.is_verified)
        print('is_banned:', api.is_banned)
        print('verified_at:', api.verified_at)
        print('created_at:', api.created_at)
        print('modified_at:', api.modified_at)
        print('-----------------------------------------\n')

        if api.address:
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
                web3 = Web3(HTTPProvider('http://localhost:8545'))
                alphabet = string.ascii_letters + string.digits
                password = ''.join(secrets.choice(alphabet) for _ in range(30))
                address = web3.personal.newAccount(password)

                # Generate QR code
                img = qrcode.make(address)
                file_name = address + '.png'
                file_path = '/images/qrcode/api/' + file_name
                img.save(settings.MEDIA_ROOT + file_path)

                # Save API object
                api.address = address
                api.password = password
                api.qrcode = file_path
                api.modified_at = timezone.now()
                api.save()
        except Exception as e:
            print('\nError:')
            print(e)
            print('\nEthereum アカウントの作成に失敗しました。')
            sys.exit(1)

        print('\nEthereum アカウントを作成しました！')
        print('Address:', api.address)
        print('Password:', api.password)
        print('QR code:', api.qrcode)

        print('\n認証を行うには次のコマンドを実行してください:')
        print(f'  > python manage.py verify_api {api_id}')
