from django.conf.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from .views import *

app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='user')
router.register(r'eth_accounts', EthAccountViewSet, base_name='eth_account')
router.register(r'transactions', TransactionViewSet, base_name='transaction')
router.register(r'eth_transactions', EthTransactionViewSet, base_name='eth_transaction')
router.register(r'contracts', ContractViewSet, base_name='contract')

urlpatterns = [
    path('', include(router.urls)),
    path('token-auth/', obtain_jwt_token),
    path('token-refresh/', refresh_jwt_token),
    path('token-verify/', verify_jwt_token),
    path('register/', RegisterView.as_view()),
]
