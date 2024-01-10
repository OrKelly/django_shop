from django.shortcuts import render
from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    #Регистрация пользователя
    path('register/', views.register_user, name='register'),
    path('email-verification-sent/',
         lambda request: render(
             request, 'account/email/email-verification-sent.html'),
         name='email-verification-sent'),

    #Авторизация и выход из аккаунта
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_user, name='dashboard'),
    path('profile-management/', views.profile_user, name='profile-management'),
    path('delete-user/', views.delete_user, name='delete-user'),

]