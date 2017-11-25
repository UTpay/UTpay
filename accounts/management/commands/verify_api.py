from django.core.management.base import BaseCommand
from django.utils import timezone
import sys

from accounts.models import Api

class Command(BaseCommand):
    help = 'Verify the user defined API.'

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

        if api.is_verified:
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
            api.is_verified = True
            api.verified_at = timezone.now()
            api.modified_at = timezone.now()
            api.save()
        except Exception as e:
            print('\nError:')
            print(e)
            print('\n認証に失敗しました。')
            sys.exit(1)

        print('\n認証しました！')
