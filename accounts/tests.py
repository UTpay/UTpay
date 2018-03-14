import secrets
import string
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from web3 import Web3, HTTPProvider

from .models import Activate, Account, EthAccount


class UserModelTests(TestCase):
    def create_user(self):
        username = 'test'
        email = 'test@example.com'
        password = 'hogehoge'

        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create Activate
        activate_key = self.create_activate_key()
        activate = Activate(user=user, key=activate_key)
        activate.save()

        # Create Account
        ut_address = self.make_ut_address()
        while Account.objects.filter(address=ut_address).exists():
            ut_address = self.make_ut_address()
        qrcode_path = '/images/qrcode/account/' + ut_address + '.png'
        Account.objects.create(user=user, address=ut_address, qrcode=qrcode_path)

        # Create EthAccount
        w3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
        password = self.make_random_password(length=30)
        eth_address = w3.personal.newAccount(password)
        qrcode_path = '/images/qrcode/eth_account/' + eth_address + '.png'
        EthAccount.objects.create(user=user, address=eth_address, password=password, qrcode=qrcode_path)

    @staticmethod
    def create_activate_key():
        """
        ランダムな文字列を生成
        :return str: UUID
        """
        return uuid.uuid4().hex

    @staticmethod
    def make_ut_address():
        """
        ランダムな42文字のUTアドレスを生成 (bitcoin base58)
        :return str: address
        """
        base58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        address = 'UT' + ''.join(secrets.choice(base58_alphabet) for _ in range(40))
        return address

    @staticmethod
    def make_random_password(length):
        """
        ランダムなパスワードを生成
        :param int length: パスワードの文字数
        :return str: password
        """
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def test_is_empty(self):
        users = User.objects.all()
        self.assertEqual(users.count(), 0)

    def test_is_not_empty(self):
        self.create_user()
        users = User.objects.all()
        self.assertEqual(users.count(), 1)

    def test_user_size_equals_eth_account_size(self):
        self.create_user()
        users = User.objects.all()
        eth_accounts = EthAccount.objects.all()
        self.assertEqual(users.count(), eth_accounts.count())

    def test_saving_and_retrieving_user(self):
        self.create_user()
        users = User.objects.all()
        user = users[0]
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.check_password('hogehoge'), True)
