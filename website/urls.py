from django.conf.urls import url

from .views import *

app_name = 'website'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^transfer/$', TransferView.as_view(), name='transfer')
]
