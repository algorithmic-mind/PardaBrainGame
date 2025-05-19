from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('login_otp/', views.LoginOTP.as_view(), name='login_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]