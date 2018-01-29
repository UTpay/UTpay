from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Activate(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    key = models.CharField('Key', max_length=191, unique=True)
    created_at = models.DateTimeField('作成日時', default=timezone.now)

# Ethereum account
class EthAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
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
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    eth_account = models.ForeignKey(EthAccount, on_delete=models.PROTECT)
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

# User defined function
class Contract(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    address = models.CharField('Address', max_length=42, unique=True, null=True, blank=True)
    password = models.CharField('Password', max_length=30, null=True, blank=True)
    qrcode = models.ImageField('QR code', upload_to='images/qrcode/contract/', null=True, blank=True)
    name = models.CharField('名前', max_length=255)
    description = models.TextField('説明', null=True, blank=True, help_text='他の利用者に公開されます。')
    code = models.TextField('ソースコード', default='pass', help_text='変数 `tx_hash`, `from_address`, `to_address`, `amount`, `amount_fixed` を使用できます。')
    is_active = models.BooleanField('有効', default=True)
    is_verified = models.BooleanField('認証済み', default=False)
    is_banned = models.BooleanField('禁止', default=False)
    verified_at = models.DateTimeField('認証日時', null=True, blank=True)
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    modified_at = models.DateTimeField('変更日時', default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Contract'
        verbose_name_plural = 'Contracts'
