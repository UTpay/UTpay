from django.contrib.auth.models import User
from rest_framework import serializers
from web3 import Web3, HTTPProvider
import secrets
import string

from accounts.models import *

class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        # Create User
        user = User.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])

        # Create EthAccount
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        password = self.make_random_password(length=30)
        address = web3.personal.newAccount(password)
        eth_account = EthAccount.objects.create(user=user, address=address, password=password)

        return user

    def make_random_password(self, length):
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

class EthAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = EthAccount
        fields = ('id', 'user', 'address')

class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    eth_account = EthAccountSerializer()

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'eth_account', 'tx_hash', 'from_address', 'to_address', 'amount', 'gas', 'gas_price', 'value', 'network_id', 'is_active', 'created_at')
