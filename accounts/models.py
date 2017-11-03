from django.db import models

# Ethereum Account
class Account(models.Model):
    user = models.ForeignKey(User, 'User')
    address_lower = models.CharField('Address (lowercase)', max_length=42)
    address_upper = models.CharField('Address (uppercase)', max_length=42)
    password = models.CharField('Password', max_length=30)
    privatekey = models.CharField('Private Key', max_length=64)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
