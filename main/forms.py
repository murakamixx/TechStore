from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={"placeholder": "username", "autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            "username": "Имя пользователя",
            "password1": "Пароль",
            "password2": "Повторите пароль",
        }
        placeholders = {
            "username": "tech_user",
            "password1": "••••••••",
            "password2": "••••••••",
        }
        for field_name, field in self.fields.items():
            field.label = labels.get(field_name, field.label)
            field.help_text = ""
            if field_name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[field_name]
