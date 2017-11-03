from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='この項目は任意です。')
    last_name = forms.CharField(max_length=30, required=False, help_text='この項目は任意です。')
    email = forms.EmailField(max_length=254, help_text='この項目は必須です。有効なメールアドレスを入力してください。')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
