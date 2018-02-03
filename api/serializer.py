from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import serializers
from web3 import Web3, HTTPProvider
import secrets
import string
import uuid
import qrcode

from accounts.models import *

class DateTimeFieldAware(serializers.DateTimeField):
    """
    Class to make output of a DateTime Field timezone aware
    """
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldAware, self).to_representation(value)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        # Create User (仮登録)
        user = User.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'], is_active=False)

        # Create Activate
        activate_key = self.create_activate_key()
        activate = Activate(user=user, key=activate_key)
        activate.save()

        # Create Account
        ut_address = self.make_ut_address()
        while Account.objects.filter(address=ut_address).exists():
            ut_address = self.make_ut_address()
        qrcode_path = self.make_qrcode(ut_address, file_dir='/images/qrcode/account/')
        account = Account.objects.create(user=user, address=ut_address, qrcode=qrcode_path)

        # Create EthAccount
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        password = self.make_random_password(length=30)
        eth_address = web3.personal.newAccount(password)
        qrcode_path = self.make_qrcode(eth_address, file_dir='/images/qrcode/eth_account/')
        eth_account = EthAccount.objects.create(user=user, address=eth_address, password=password, qrcode=qrcode_path)

        # Send activation email
        # FIXME: 自動で `base_url` を取得したい
        base_url = 'http://127.0.0.1:8000'
        activation_url = base_url + reverse('accounts:activation', args=[activate_key])
        user.email_user(
            '[UTpay] Please verify your email',
            f'@{user.username} さん\n\nこの度は、UTpay にご登録いただきありがとうございます。\n以下のURLにアクセスして、登録を確認してください。\n\n{activation_url}\n\n--\nUTpay <https://utpay.net>\ninfo@utpay.net'
        )

        return user

    def validate_email(self, email):
        """
        :param str email:
        :return str: cleaned email
        """
        domain = email.split('@')[1]
        if 'u-tokyo.ac.jp' not in domain:
            raise serializers.ValidationError('東京大学のドメイン(u-tokyo.ac.jp)が含まれていません。')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('既に登録されているメールアドレスです。')
        return email

    def create_activate_key(self):
        """
        ランダムな文字列を生成
        :return str: UUID
        """
        return uuid.uuid4().hex

    def make_ut_address(self):
        """
        ランダムな42文字のUTアドレスを生成 (bitcoin base58)
        :return str: address
        """
        base58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        address = 'UT' + ''.join(secrets.choice(base58_alphabet) for _ in range(40))
        return address

    def make_random_password(self, length):
        """
        ランダムなパスワードを生成
        :param int length: パスワードの文字数
        :return str: password
        """
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def make_qrcode(self, address, file_dir):
        """
        QRコードを生成
        :param str address:
        :param str file_dir:
        :return str: file path
        """
        img = qrcode.make(address)
        file_name = address + '.png'
        file_path = file_dir + file_name
        img.save(settings.MEDIA_ROOT + file_path)
        return file_path

class EthAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = EthAccount
        fields = ('id', 'user', 'address', 'qrcode')

class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    eth_account = EthAccountSerializer()
    amount_fixed = serializers.SerializerMethodField()
    created_at = DateTimeFieldAware(format="%Y/%m/%d %H:%M:%S")

    def get_amount_fixed(self, obj):
        num_suffix = 1000
        return obj.amount / num_suffix

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'eth_account', 'tx_hash', 'from_address', 'to_address', 'amount', 'amount_fixed', 'gas', 'gas_price', 'value', 'network_id', 'is_active', 'created_at')

class ContractSerializer(serializers.ModelSerializer):
    verified_at = DateTimeFieldAware(format="%Y/%m/%d %H:%M:%S")
    created_at = DateTimeFieldAware(format="%Y/%m/%d %H:%M:%S")
    modified_at = DateTimeFieldAware(format="%Y/%m/%d %H:%M:%S")

    class Meta:
        model = Contract
        fields = ('id', 'address', 'qrcode', 'name', 'description', 'code', 'is_active', 'is_verified', 'is_banned', 'verified_at', 'created_at', 'modified_at')
