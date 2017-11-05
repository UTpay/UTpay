from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from web3 import Web3, HTTPProvider
import json

from accounts.models import EthAccount

class SendForm(forms.Form):
    address = forms.CharField(label='宛先', max_length=42, widget=forms.TextInput(attrs={'placeholder': '0x...'}))
    amount = forms.FloatField(label='金額 (UTC)', min_value=0.001, widget=forms.TextInput(attrs={'placeholder': '例) 10.123'}))
    fee = forms.FloatField(label='手数料 (UTC)', widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    balance = forms.FloatField(label='送金可能額 (UTC)', min_value=0, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

    def __init__(self, user, data=None, initial=None):
        self.user = user
        super(SendForm, self).__init__(data=data, initial=initial)

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        if not self.user.check_password(password):
            raise ValidationError('パスワードが違います。')
        return password

    def clean_address(self):
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        address = self.cleaned_data.get('address', None)
        if not web3.isAddress(address):
            raise ValidationError('正しいアドレスを入力してください。')
        return address

    def clean_amount(self):
        eth_account = EthAccount.objects.get(user=self.user)

        # Get UTCoin balance
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        abi = self.load_abi(settings.ARTIFACT_PATH)
        UTCoin = web3.eth.contract(abi=abi, address=settings.UTCOIN_ADDRESS)
        balance = UTCoin.call().balanceOf(eth_account.address)

        amount = self.cleaned_data.get('amount', None)
        if balance < amount:
            raise ValidationError('送金可能額を超えています。')
        return amount

    def load_abi(self, file_path):
        artifact = open(file_path, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        return abi
