from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Contract

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        label='ユーザー名',
        help_text='半角英数字、@/./+/-/_ で150文字以下にしてください。',
    )
    first_name = forms.CharField(
        max_length=30,
        label='名 (First name)',
    )
    last_name = forms.CharField(
        max_length=30,
        label='姓 (Last name)',
    )
    email = forms.EmailField(
        max_length=254,
        label='メールアドレス',
        help_text='有効な東京大学のメールアドレス(u-tokyo.ac.jp)を入力してください。',
    )
    password1 = forms.CharField(
        label='パスワード',
        help_text='パスワードは最低8文字以上必要です。数字だけのパスワードやよく使われるパスワードにはできません。',
    )
    password2 = forms.CharField(
        label='パスワード (確認)',
        help_text='確認のため、再度同じパスワードを入力してください。',
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class ContractForm(ModelForm):
    class Meta:
        model = Contract
        fields = ['name', 'description', 'code']
