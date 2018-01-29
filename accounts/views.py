from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db import transaction
from django.urls import reverse
from web3 import Web3, HTTPProvider
import secrets
import string
import uuid

from .models import *
from .forms import *

class SignUpView(View):
    template_name = 'signup.html'

    def get(self, request):
        form = SignUpForm()
        context = {
            'title': 'サインアップ',
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save objects
            with transaction.atomic():
                # Create User (仮登録)
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                # Create Activate
                activate_key = self.create_activate_key()
                activate = Activate(user=user, key=activate_key)
                activate.save()

                # Create EthAccount
                web3 = Web3(HTTPProvider('http://localhost:8545'))
                password = self.make_random_password(length=30)
                address = web3.personal.newAccount(password)
                eth_account = EthAccount.objects.create(user=user, address=address, password=password)

                # Send activation email
                base_url = "/".join(request.build_absolute_uri().split("/")[:3])
                activation_url = base_url + reverse('accounts:activation', args=[activate_key])
                user.email_user(
                    '[UTpay] Please verify your email',
                    f'@{user.username} さん\n\nこの度は、UTpay にご登録いただきありがとうございます。\n以下のURLにアクセスして、登録を確認してください。\n\n{activation_url}\n\n--\nUTpay <https://utpay.net>\ninfo@utpay.net'
                )
                # TODO: リダイレクト先にメッセージを表示

            return redirect('website:index')
        else:
            context = {
                'title': 'サインアップ',
                'form': form,
            }
            return render(request, self.template_name, context)

    def make_random_password(self, length):
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    # Create random string
    def create_activate_key(self):
        return uuid.uuid4().hex

class ActivationView(View):
    template_name = 'activation.html'

    def get(self, request, key):
        activate = get_object_or_404(Activate, key=key)
        user = activate.user

        # アカウントを有効化
        if user.is_active == False:
            user.is_active = True
            user.save()

        context = {
            'title': '本登録完了',
        }
        return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
class MyPageView(View):
    template_name = 'mypage.html'

    def get(self, request):
        context = {
            'title': 'マイページ',
        }
        return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
class ContractView(View):
    template_name = 'contract.html'

    def get(self, request):
        contracts = Contract.objects.filter(user=request.user, is_banned=False)
        context = {
            'title': 'コントラクト',
            'contracts': contracts,
        }
        return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
class ContractRegisterView(View):
    template_name = 'contract_register.html'

    def get(self, request):
        form = ContractForm
        context = {
            'title': 'コントラクトを登録する',
            'form': form,
        }
        return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
class ContractDetailView(View):
    template_name = 'contract_detail.html'

    def get(self, request, address):
        contract = get_object_or_404(Contract, user=request.user, address=address)
        context = {
            'title': contract.name,
            'contract': contract,
        }
        return render(request, self.template_name, context)
