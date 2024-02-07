from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count
from django.db.models.functions import Round
from django.shortcuts import redirect, render
from django.urls import reverse
from django_email_verification import send_email

from .forms import UserCreateForm, LoginForm, UserUpdateForm
from payment.models import Order, ShippingAddress
from payment.forms import ShippingAddressForm

User = get_user_model()


def register_user(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)

        if form.is_valid():
            form.save(commit=False)
            user_email = form.cleaned_data.get('email')
            user_username = form.cleaned_data.get('username')
            user_password = form.cleaned_data.get('password1')

            # creating new user
            user = User.objects.create_user(
                username=user_username, email=user_email, password=user_password
            )

            user.is_active = False

            send_email(user)  # sending email for register confirmation

            return redirect('/account/email-verification-sent/')
    else:
        form = UserCreateForm()
    return render(request, 'account/registration/register.html', {'form': form})


def login_user(request):
    form = LoginForm()

    if request.user.is_authenticated:
        return redirect('shop:products')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('shop:products')
        else:
            messages.info(request, 'Неверный логин или пароль!')
            return redirect('account:login')

    return render(request, 'account/login/login.html', {'form': form})


def logout_user(request):
    session_keys = list(request.session.keys())
    for key in session_keys:    # clear session
        if key == 'session_key':
            continue
        del request.session[key]
    logout(request)
    return redirect('shop:products')


@login_required(login_url='account:login')
def dashboard_user(request):
    # get information about all user's orders, total cost and count of them
    orders = Order.objects.select_related('user').filter(user=request.user).aggregate(summ=Round(Sum(F('amount'))),
                                                                                      total=Count('id'))
    user_orders = Order.objects.select_related('user').filter(user=request.user).order_by('created')
    try:
        shipping_address = ShippingAddress.objects.get(user=request.user)
    except ShippingAddress.DoesNotExist:
        shipping_address = None
    form = ShippingAddressForm(instance=shipping_address)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('account:dashboard')

    return render(request, 'account/dashboard/dashboard.html',
                  {'orders': orders, 'form': form, 'user_orders': user_orders})


@login_required(login_url='account:login')
def profile_user(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('account:dashboard')
    else:
        form = UserUpdateForm(request.GET)
    context = {
        'form': form
    }
    return render(request, 'account/dashboard/profile-management.html', context)


@login_required(login_url='account:login')
def delete_user(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        user.delete()
        return redirect('shop:products')
    return render(request, 'account/dashboard/account-delete.html')
