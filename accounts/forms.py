from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # تغییر برچسب‌های فارسی
        self.fields['username'].label = "نام کاربری"
        self.fields['email'].label = "ایمیل"
        self.fields['password1'].label = "رمز عبور"
        self.fields['password2'].label = "تکرار رمز عبور"

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        # تغییر برچسب‌های فارسی
        self.fields['username'].label = "نام کاربری"
        self.fields['email'].label = "ایمیل"
        self.fields['first_name'].label = "نام"
        self.fields['last_name'].label = "نام خانوادگی"