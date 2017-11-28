from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    url(r'^signup/$', SignUpView.as_view(), name='signup'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    url(r'^mypage/$', MyPageView.as_view(), name='mypage'),
    url(r'^mypage/contract/$', ContractView.as_view(), name='contract'),
    url(r'^mypage/contract/register/$', ContractRegisterView.as_view(), name='contract_register'),
    url(r'^mypage/contract/(?P<address>\w+)/$', ContractDetailView.as_view(), name='contract_detail'),
]
