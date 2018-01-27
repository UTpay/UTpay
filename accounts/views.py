from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db import transaction
from web3 import Web3, HTTPProvider
import secrets
import string

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
                # Create User
                user = form.save()

                # Create EthAccount
                web3 = Web3(HTTPProvider('http://localhost:8545'))
                password = self.make_random_password(length=30)
                address = web3.personal.newAccount(password)
                eth_account = EthAccount.objects.create(user=user, address=address, password=password)

            # Log in
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('accounts:mypage')
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
        context = {
            'title': 'コントラクト',
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
