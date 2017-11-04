from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Ethereum account
class EthAccount(models.Model):
    user = models.ForeignKey(User)
    address = models.CharField('Address', max_length=42)
    password = models.CharField('Password', max_length=30)
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    modified_at = models.DateTimeField('変更日時', default=timezone.now)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'ETH Account'
        verbose_name_plural = 'ETH Accounts'

# Transaction information
class Transaction(models.Model):
    user = models.ForeignKey(User)
    eth_account = models.ForeignKey(EthAccount)
    tx_hash = models.CharField('TxHash', max_length=66)
    from_address = models.CharField('From', max_length=42)
    to_address = models.CharField('To', max_length=42)
    amount = models.BigIntegerField('Amount', help_text='UTC')
    gas = models.BigIntegerField('Gas')
    gas_price = models.BigIntegerField('Gas Price')
    value = models.BigIntegerField('Value')
    network_id = models.IntegerField('Network ID')
    is_active = models.BooleanField('有効', default=True)
    created_at = models.DateTimeField('作成日時', default=timezone.now)

    def __str__(self):
        return self.tx_hash

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
