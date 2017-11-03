from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings
from web3 import Web3, HTTPProvider
import json

from .models import *
from accounts.models import EthAccount
from .forms import *

class IndexView(TemplateView):
    template_name = 'index.html'

class SendView(View):
    template_name = 'send.html'

    def get(self, request):
        eth_account = get_object_or_404(EthAccount, user=request.user)

        # Get balance of UTCoin
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        abi = self.load_abi(settings.ARTIFACT_PATH)
        UTCoin = web3.eth.contract(abi=abi, address=settings.UTCOIN_ADDRESS)
        balance = UTCoin.call().balanceOf(eth_account.address)

        # TODO: Set fee
        fee = 0.001

        form = SendForm(initial={'fee': fee, 'balance': balance})

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
