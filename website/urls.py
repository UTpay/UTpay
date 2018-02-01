from django.urls import path

from .views import *

app_name = 'website'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('transfer/', TransferView.as_view(), name='transfer')
]
