from django.conf.urls import url

from .views import *

app_name = 'website'

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^send/$', SendView.as_view(), name='send')
]
