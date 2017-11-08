from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import permissions, generics, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from django_filters.rest_framework import DjangoFilterBackend
from web3 import Web3, HTTPProvider
import json

from .serializer import *

class RegisterView(generics.CreateAPIView):
    """
    Create User
    """
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.id)

class EthAccountViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EthAccountSerializer

    def get_queryset(self):
        return EthAccount.objects.filter(user=self.request.user)

    @detail_route()
    def get_balance(self, request, pk=None):
        eth_account = get_object_or_404(EthAccount, address=pk)
        address = eth_account.address

        # Get UTCoin balance
        num_suffix = 1000
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        abi = self.load_abi(settings.ARTIFACT_PATH)
        UTCoin = web3.eth.contract(abi=abi, address=settings.UTCOIN_ADDRESS)
        balance_int = UTCoin.call().balanceOf(address)
        balance = float(balance_int / num_suffix)

        context = {
            'address': address,
            'balance': balance,
            'balance_int': balance_int
        }
        return Response(context)

    def load_abi(self, file_path):
        artifact = open(file_path, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        return abi

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TransactionSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('user', 'eth_account', 'tx_hash', 'from_address', 'to_address', 'amount', 'gas', 'gas_price', 'value', 'network_id', 'is_active', 'created_at')
    ordering_fields = ('amount', 'gas', 'gas_price', 'value', 'created_at')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    @list_route(methods=['post'])
    @transaction.atomic
    def transfer(self, request):
        eth_account = get_object_or_404(EthAccount, user=request.user)
        from_address = eth_account.address
        num_suffix = 1000
        fee = 0.001

        # Receive params
        to_address = request.POST.get('address', None)
        amount = request.POST.get('amount', None)
        if not (to_address and amount):
            error_msg = 'アドレスまたは金額が入力されていません。'
            print('Error:', error_msg)
            context = {
                'success': False,
                'detail': error_msg
            }
            return Response(context)

        amount = float(amount)
        amount_int = int(amount * num_suffix)

        # Validate address
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        if not web3.isAddress(to_address):
            error_msg = '無効なアドレスです。'
            print('Error:', error_msg)
            context = {
                'success': False,
                'detail': error_msg
            }
            return Response(context)

        # Validate amount
        # Get UTCoin balance
        abi = self.load_abi(settings.ARTIFACT_PATH)
        UTCoin = web3.eth.contract(abi=abi, address=settings.UTCOIN_ADDRESS)
        balance = UTCoin.call().balanceOf(from_address)

        if balance < amount + fee:
            error_msg = '残高が不足しています。'
            print('Error:', error_msg)
            context = {
                'success': False,
                'detail': error_msg
            }
            return Response(context)

        # Transfer UTCoin
        if web3.personal.unlockAccount(from_address, eth_account.password, duration=hex(300)):
            try:
                tx_hash = UTCoin.transact({'from': from_address}).transfer(to_address, amount_int)

                # Create Transaction
                transaction_info = web3.eth.getTransaction(tx_hash)
                transaction = Transaction.objects.create(
                    user=request.user,
                    eth_account=eth_account,
                    tx_hash=tx_hash,
                    from_address=from_address,
                    to_address=to_address,
                    amount=amount_int,
                    gas=transaction_info['gas'],
                    gas_price=transaction_info['gasPrice'],
                    value=transaction_info['value'],
                    network_id=transaction_info['networkId']
                )
            except Exception as e:
                print(e)
                error_msg = 'トランザクションに失敗しました。'
                print('Error:', error_msg)
                context = {
                    'success': False,
                    'detail': error_msg
                }
                return Response(context)
        else:
            error_msg = 'アカウントのアンロックに失敗しました。'
            print('Error:', error_msg)
            context = {
                'success': False,
                'detail': error_msg
            }
            return Response(context)

        context = {
            'success': True,
            'address': to_address,
            'amount': amount,
            'fee': fee,
            'transaction': TransactionSerializer(transaction).data
        }
        return Response(context, status=status.HTTP_201_CREATED)

    def load_abi(self, file_path):
        artifact = open(file_path, 'r')
        json_dict = json.load(artifact)
        abi = json_dict['abi']
        return abi
