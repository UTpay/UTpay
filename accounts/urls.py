from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    url(r'^signup/$', SignUpView.as_view(), name='signup'),
]
