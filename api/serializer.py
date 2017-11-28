from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers
from web3 import Web3, HTTPProvider
import secrets
import string
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

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        # Create User
        user = User.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])

        # Generate random password and address
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        password = self.make_random_password(length=30)
        address = web3.personal.newAccount(password)

        # Generate QR code
        img = qrcode.make(address)
        file_name = address + '.png'
        file_path = '/images/qrcode/' + file_name
        img.save(settings.MEDIA_ROOT + file_path)

        # Create EthAccount
        eth_account = EthAccount.objects.create(user=user, address=address, password=password, qrcode=file_path)

        return user

    def make_random_password(self, length):
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

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
