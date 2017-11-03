from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Ethereum Account
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
