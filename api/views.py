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
        to_address = request.POST['address']
        amount = float(request.POST['amount'])
        amount_int = int(amount * num_suffix)

        # Validate address
        web3 = Web3(HTTPProvider('http://localhost:8545'))
        if not web3.isAddress(to_address):
            error_msg = 'invalid address'
            print(error_msg)
            context = {
                'success': False,
                'detail': error_msg
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        # Validate amount
        # Get UTCoin balance
        abi = self.load_abi(settings.ARTIFACT_PATH)
        UTCoin = web3.eth.contract(abi=abi, address=settings.UTCOIN_ADDRESS)
        balance = UTCoin.call().balanceOf(from_address)

        if balance < amount + fee:
            error_msg = 'insufficient funds'
            print(error_msg)
            context = {
                'success': False,
                'detail': error_msg
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

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
                error_msg = 'transaction failed'
                print(error_msg)
                context = {
                    'success': False,
                    'detail': error_msg
                }
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_msg = 'failed to unlock account'
            print(error_msg)
            context = {
                'success': False,
                'detail': error_msg
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

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
