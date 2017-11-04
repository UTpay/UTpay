from django.contrib import admin

from .models import *

class EthAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address', 'password', 'created_at', 'modified_at')
    list_filter = ('user', 'created_at', 'modified_at')
    ordering = ('id',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'eth_account', 'tx_hash', 'from_address', 'to_address', 'amount', 'gas', 'gas_price', 'value', 'network_id', 'is_active', 'created_at')
    list_filter = ('user', 'eth_account', 'from_address', 'to_address', 'amount', 'gas', 'gas_price', 'value', 'network_id', 'is_active', 'created_at')
    ordering = ('id',)

admin.site.register(EthAccount, EthAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
