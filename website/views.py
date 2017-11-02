from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from .models import *

class IndexView(TemplateView):
    template_name = 'index.html'
