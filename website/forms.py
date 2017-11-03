from django import forms

class SendForm(forms.Form):
    address = forms.CharField(label='宛先', max_length=42, widget=forms.TextInput(attrs={'placeholder': '0x...'}))
    amount = forms.FloatField(label='金額 (UTC)', min_value=0.001, widget=forms.TextInput(attrs={'placeholder': '例) 10.123'}))
    fee = forms.FloatField(label='手数料 (UTC)', widget=forms.TextInput(attrs={'disabled': 'disabled'}))
    balance = forms.FloatField(label='送金可能額 (UTC)', min_value=0, widget=forms.TextInput(attrs={'disabled': 'disabled'}))
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())
