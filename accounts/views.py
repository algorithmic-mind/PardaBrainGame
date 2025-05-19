from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.messages import error
from .models import OtpCode
from utils.sms import send_otp
from random import randint


class CustomLoginView(View):
    
    def get(self,request):
        return render(request,'accounts/login.html')

    def post(self,request):
        phone = request.POST['phone']

        if User.objects.filter(username=phone).exists():
            user = User.objects.get(username=phone)
            random_otp_code = randint(1000,9999)
            new_otp = OtpCode(username_phone=user,code=random_otp_code)
            new_otp.save()
            send_otp(phone=phone,code=random_otp_code)

            request.session['phone'] = phone
            request.session.set_expiry(180)
            if user.first_name:
                return redirect('accounts:login_otp')
            else:
                return redirect('accounts:register')

        else:
            request.session['phone'] = phone
            new_user = User.objects.create(username=phone)
            return redirect('accounts:register')




class LoginOTP(View):

    def get(self,request):
        return render(request,'accounts/login_otp.html')

    def post(self,request):

        phone = request.session.get('phone')
        if phone:
            otp = request.POST['otp']
            user = User.objects.get(username=phone)
            latest_user_otp = OtpCode.objects.filter(username_phone=user).last()
            latest_user_otp = latest_user_otp.code

            if latest_user_otp == otp:
                
                if request.session.get('f_name') and request.session.get('l_name'):
                    user.first_name = request.session.get('f_name')
                    user.last_name = request.session.get('l_name')
                    user.save()
                    
                OtpCode.objects.filter(username_phone=user).delete()
                login(request,user=user)
                return redirect('quiz:dashboard')
            else:
                error(request,'کد احراز هویت صحیح نمی باشد')
                return redirect('accounts:login_otp')

        else:
            return redirect('accounts:login')




        return HttpResponse(latest_user_otp)
    
    
    

class RegisterView(View):

    def get(self,request):
        phone = request.session.get('phone')
        if phone:
            return render(request,'accounts/register.html')
        else:
            return redirect("accounts:login")

    def post(self,request):

        phone = request.POST['phone']
        f_name = request.POST['f_name']
        l_name = request.POST['l_name']
        new_user = User.objects.get(username=phone)
        random_otp_code = randint(1000,9999)
        new_otp = OtpCode(username_phone=new_user,code=random_otp_code)
        new_otp.save()
        send_otp(phone=phone,code=random_otp_code)


        request.session['f_name'] = f_name
        request.session['l_name'] = l_name

        return redirect('accounts:login_otp')

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
    