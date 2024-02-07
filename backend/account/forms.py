from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput

User = get_user_model()


class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(UserCreateForm, self).__init__(*args, **kwargs)

        self.fields['email'].label = 'Ваш email адрес'
        self.fields['email'].required = True
        self.fields['username'].label = 'Ваш логин'
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email уже занят!")
        if len(email) > 254:
            raise forms.ValidationError("Email слишком длинный!")

        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control'}))


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(UserUpdateForm, self).__init__(*args, **kwargs)

        self.fields['email'].label = 'Ваш email'
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email уже занят!")
        if len(email) > 254:
            raise forms.ValidationError("Email слишком длинный!")

        return email

    class Meta:
        model = User
        fields = ['username', 'email']
        exclude = ('password1', 'password2')
