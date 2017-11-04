from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet, base_name='user')
router.register(r'eth_accounts', EthAccountViewSet, base_name='eth_account')
router.register(r'transactions', TransactionViewSet, base_name='transaction')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^token-auth/', obtain_jwt_token),
    url(r'^token-refresh/', refresh_jwt_token),
    url(r'^token-verify/', verify_jwt_token),
    url(r'^register/$', RegisterView.as_view()),
]
