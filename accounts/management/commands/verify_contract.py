from django.core.management.base import BaseCommand
from django.utils import timezone
import sys

from accounts.models import Contract

class Command(BaseCommand):
    help = 'Verify the contract.'

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

        if contract.is_verified:
            print('既に認証されています。')
            sys.exit(1)

        # 確認
        print('注意: 認証を行うとユーザが利用可能な状態になります。')
        confirm = input('認証を行いますか？(y/N): ')
        if confirm != 'y':
            print('キャンセルしました。')
            sys.exit(0)

        # 認証
        try:
            contract.is_verified = True
            contract.verified_at = timezone.now()
            contract.modified_at = timezone.now()
            contract.save()
        except Exception as e:
            print('\nError:')
            print(e)
            print('\n認証に失敗しました。')
            sys.exit(1)

        print('\n認証しました！')
