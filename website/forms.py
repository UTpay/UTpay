from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from web3 import Web3, HTTPProvider
import json

from accounts.models import Account


class TransferForm(forms.Form):
    address = forms.CharField(
        label='宛先',
        max_length=42,
        help_text='例) UT... or 0x...',
        widget=forms.TextInput(attrs={'class': 'mdl-textfield__input'}),
    )
    amount = forms.FloatField(
        label='金額 (UTC)',
        min_value=0.001,
        help_text='例) 10.123',
        widget=forms.NumberInput(attrs={'class': 'mdl-textfield__input', 'step': '0.001'}),
    )
    fee = forms.FloatField(
        label='手数料 (UTC)',
        widget=forms.TextInput(attrs={'class': 'mdl-textfield__input', 'readonly': 'readonly'}),
    )
    balance = forms.FloatField(
        label='送金可能額 (UTC)',
        min_value=0,
        widget=forms.TextInput(attrs={'class': 'mdl-textfield__input', 'readonly': 'readonly'}),
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'mdl-textfield__input'}),
    )

    def __init__(self, user, data=None, initial=None):
        self.user = user
        super(TransferForm, self).__init__(data=data, initial=initial)

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        if password is None:
            raise ValidationError('パスワードを入力してください。')

        if not self.user.check_password(password):
            raise ValidationError('パスワードが違います。')

        return password

    def clean_address(self):
        address = self.cleaned_data.get('address', None)
        if address is None:
            raise ValidationError('アドレスを入力してください。')

        web3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
        if self.is_ut_address(address):
            if address != self.user.account.address:
                return address
        elif web3.isAddress(address):
            if address != self.user.ethaccount.address:
                return address

        raise ValidationError('正しいアドレスを入力してください。')

    def clean_amount(self):
        account = Account.objects.get(user=self.user)
        amount = self.cleaned_data.get('amount', None)
        if amount is None:
            raise ValidationError('金額を入力してください。')

        if account.balance < amount:
            raise ValidationError('送金可能額を超えています。')

        return amount

    @staticmethod
    def load_abi(file_path):
        """
        :param str file_path:
        :return dict: abi
        """
        artifact = open(file_path, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        return abi

    @staticmethod
    def is_ut_address(address):
        """
        :param str address:
        :return bool:
        """
        if address[0:2] == 'UT' and len(address) == 42:
            if Account.objects.filter(address=address).exists():
                return True
        return False
