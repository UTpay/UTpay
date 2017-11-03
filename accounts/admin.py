from django.contrib import admin

from .models import *

class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address_upper', 'password', 'privatekey', 'created_at', 'modified_at')
    list_filter = ('user', 'created_at', 'modified_at')
    ordering = ('id',)

admin.site.register(Account, AccountAdmin)
