from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages

from .forms import UserRegisterForm, UserUpdateForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ورود به سیستم'
        return context

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'حساب کاربری برای {username} با موفقیت ایجاد شد! اکنون می‌توانید وارد شوید.')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
        'title': 'ثبت نام'
    }
    return render(request, 'accounts/register.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات حساب کاربری شما با موفقیت به‌روزرسانی شد!')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'title': 'پروفایل کاربری'
    }
    return render(request, 'accounts/profile.html', context)


def logout_view(request):
    logout(request)
    return redirect('quiz:home')
    