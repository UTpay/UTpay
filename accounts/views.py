from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.views import View

from .models import *
from .forms import SignUpForm

class SignUpView(View):
    template_name = 'signup.html'

    def get(self, request):
        form = SignUpForm()
        context = {
            'title': 'Sign up',
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/') # mypage
        else:
            context = {
                'title': 'Sign up',
                'form': form
            }
            return render(request, self.template_name, context)

class MyPageView(View):
    template_name = 'mypage.html'

    def get(self, request):
        context = {
            'title': 'My page'
        }
        return render(request, self.template_name, context)
