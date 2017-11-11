from django.test import TestCase
from django.contrib.auth.models import User
from web3 import Web3, HTTPProvider
import secrets
import string
import qrcode

from .models import EthAccount

class UserModelTests(TestCase):
    def create_user(self):
        username = 'test'
        email = 'test@example.com'
        password = 'hogehoge'

        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)

        # Generate random password and address
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(30))
        address = web3.personal.newAccount(password)

        # Generate QR code
        img = qrcode.make(address)
        file_name = address + '.png'
        file_path = '/images/qrcode/' + file_name

        # Create EthAccount
        eth_account = EthAccount.objects.create(user=user, address=address, password=password, qrcode=file_path)

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
