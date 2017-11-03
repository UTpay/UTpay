from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
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
            return redirect('accounts:mypage')
        else:
            context = {
                'title': 'Sign up',
                'form': form
            }
            return render(request, self.template_name, context)

@method_decorator(login_required, name='dispatch')
class MyPageView(View):
    template_name = 'mypage.html'

    def get(self, request):
        context = {
            'title': 'My page'
        }
        return render(request, self.template_name, context)
