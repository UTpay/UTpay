from django.contrib import admin

from .models import *

class EthAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address', 'password', 'created_at', 'modified_at')
    list_filter = ('user', 'created_at', 'modified_at')
    ordering = ('id',)

admin.site.register(EthAccount, EthAccountAdmin)
