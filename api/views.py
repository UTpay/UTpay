from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import authentication, permissions, generics, status, viewsets, filters
from rest_framework_jwt.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializer import *

# Create User
class RegisterView(generics.CreateAPIView):
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
