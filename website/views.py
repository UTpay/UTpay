from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings
from django.db import transaction
from web3 import Web3, HTTPProvider
from decimal import *
import json

from .models import *
from accounts.models import EthAccount, OffChainTransaction, Transaction
from .forms import *

class IndexView(TemplateView):
    template_name = 'index.html'

@method_decorator(login_required, name='dispatch')
class TransferView(View):
    template_name = 'transfer.html'

    def get(self, request):
        form = self.init_form()

        context = {
            'title': 'コインを送る',
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = TransferForm(user=request.user, data=request.POST)
        if form.is_valid():
            to_address = form.cleaned_data['address']
            if self.is_ut_address(to_address):
                # UT address -> UT address
                from_account = request.user.account
                to_account = Account.objects.get(address=to_address)
                amount = Decimal(form.cleaned_data['amount'])

                # UTCoin 送金
                with transaction.atomic():
                    from_account.balance -= amount
                    to_account.balance += amount
                    from_account.save()
                    to_account.save()

                    # Create OffChainTransaction
                    off_chain_transaction = OffChainTransaction.objects.create(
                        user=request.user,
                        account=from_account,
                        from_address=from_account.address,
                        to_address=to_address,
                        amount=amount
                    )

            else:
                # UT address -> ETH address
                num_suffix = 1000
                from_account = request.user.account
                admin = User.objects.get(pk=1)
                admin_eth_account = admin.ethaccount
                amount = int(form.cleaned_data['amount'] * num_suffix)
                fee = 0

                # UTCoin 送金
                web3 = Web3(HTTPProvider(settings.WEB3_PROVIDER))
                abi = self.load_abi(settings.ARTIFACT_PATH)
                UTCoin = web3.eth.contract(abi=abi, address=settings.UTCOIN_ADDRESS)
                if web3.personal.unlockAccount(admin_eth_account.address, admin_eth_account.password, duration=hex(60)):
                    try:
                        tx_hash = UTCoin.transact({'from': admin_eth_account.address}).transfer(to_address, amount - fee)

                        with transaction.atomic():
                            from_account.balance -= amount
                            from_account.save()

                            # Create Transaction
                            tx_info = web3.eth.getTransaction(tx_hash)
                            tx = Transaction.objects.create(
                                user=request.user,
                                eth_account=admin_eth_account,
                                tx_hash=tx_hash,
                                from_address=admin_eth_account.address,
                                to_address=to_address,
                                amount=amount,
                                gas=tx_info['gas'],
                                gas_price=tx_info['gasPrice'],
                                value=tx_info['value'],
                                network_id=tx_info['networkId']
                        )
                    except Exception as e:
                        print(e)

                else:
                    print('failed to unlock account')

            # フォーム初期化 (送金可能額を再計算)
            form = self.init_form()

        context = {
            'title': 'コインを送る',
            'form': form
        }
        return render(request, self.template_name, context)

    def init_form(self, fee=0):
        """
        :param int fee:
        :return class 'website.forms.TransferForm':
        """
        account = self.request.user.account
        fee = str(fee)

        # 送金可能額を計算
        balance = account.balance - Decimal(fee)
        if balance < 0:
            balance = 0

        form = TransferForm(user=self.request.user, initial={'fee': fee, 'balance': balance})
        return form

    def is_ut_address(self, address):
        """
        :param str address:
        :return bool:
        """
        if address[0:2] == 'UT' and len(address) == 42:
            if Account.objects.filter(address=address).exists():
                return True
        return False

    def load_abi(self, file_path):
        """
        :param str file_path:
        :return dict: abi
        """
        artifact = open(file_path, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        return abi
