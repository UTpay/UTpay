from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Ethereum account
class EthAccount(models.Model):
    user = models.ForeignKey(User)
    address = models.CharField('Address', max_length=42, unique=True)
    password = models.CharField('Password', max_length=30)
    qrcode = models.ImageField('QR code', upload_to='images/qrcode/', null=True, blank=True)
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
    tx_hash = models.CharField('TxHash', max_length=66, unique=True)
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

# User defined API
class Api(models.Model):
    user = models.ForeignKey(User)
    address = models.CharField('Address', max_length=42, unique=True, null=True, blank=True)
    password = models.CharField('Password', max_length=30, null=True, blank=True)
    qrcode = models.ImageField('QR code', upload_to='images/qrcode/api/', null=True, blank=True)
    name = models.CharField('名前', max_length=255)
    description = models.TextField('説明', null=True, blank=True)
    code = models.TextField('ソースコード', default='pass')
    is_active = models.BooleanField('有効', default=True)
    is_verified = models.BooleanField('認証済み', default=False)
    is_banned = models.BooleanField('禁止', default=False)
    verified_at = models.DateTimeField('認証日時', null=True, blank=True)
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    modified_at = models.DateTimeField('変更日時', default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'API'
        verbose_name_plural = 'APIs'
