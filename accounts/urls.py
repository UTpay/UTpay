from django.contrib.auth import views as auth_views
from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('activation/<key>/', ActivationView.as_view(), name='activation'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('mypage/', MyPageView.as_view(), name='mypage'),
    path('mypage/contract/', ContractView.as_view(), name='contract'),
    path('mypage/contract/register/', ContractRegisterView.as_view(), name='contract_register'),
    path('mypage/contract/<address>/', ContractDetailView.as_view(), name='contract_detail'),
]
