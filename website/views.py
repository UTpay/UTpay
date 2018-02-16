from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings
from web3 import Web3, HTTPProvider
from decimal import *
import json

from .models import *
from accounts.models import EthAccount, Transaction
from .forms import *

class IndexView(TemplateView):
    template_name = 'index.html'

@method_decorator(login_required, name='dispatch')
class TransferView(View):
    template_name = 'transfer.html'

    def get(self, request):
        account = request.user.account

        # TODO: Set fee
        fee = '0'

        # 残高確認 (送金可能額)
        balance = account.balance
        if balance < 0:
            balance = 0

        form = TransferForm(user=request.user, initial={'fee': fee, 'balance': balance})

        context = {
            'title': 'コインを送る',
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        eth_account = get_object_or_404(EthAccount, user=request.user)
        from_address = eth_account.address
        num_suffix = 1000

        form = TransferForm(user=request.user, data=request.POST)
        if form.is_valid():
            to_address = form.cleaned_data['address']
            amount = int(form.cleaned_data['amount'] * num_suffix)

            # TODO: Set fee
            fee = '0'

            # Transfer UTCoin
            web3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
            abi = self.load_abi(settings.ARTIFACT_PATH)
            UTCoin = web3.eth.contract(abi=abi, address=settings.UTCOIN_ADDRESS)
            if web3.personal.unlockAccount(from_address, eth_account.password, duration=hex(300)):
                try:
                    tx_hash = UTCoin.transact({'from': from_address}).transfer(to_address, amount)

                    # Create Transaction
                    transaction_info = web3.eth.getTransaction(tx_hash)
                    transaction = Transaction.objects.create(
                        user=request.user,
                        eth_account=eth_account,
                        tx_hash=tx_hash,
                        from_address=from_address,
                        to_address=to_address,
                        amount=amount,
                        gas=transaction_info['gas'],
                        gas_price=transaction_info['gasPrice'],
                        value=transaction_info['value'],
                        network_id=transaction_info['networkId']
                    )
                except Exception as e:
                    print(e)
            else:
                print('failed to unlock account')

        context = {
            'title': 'コインを送る',
            'form': form
        }
        return render(request, self.template_name, context)

    def load_abi(self, file_path):
        artifact = open(file_path, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        return abi
