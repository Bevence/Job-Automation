from django.contrib.auth.forms import UserCreationForm
from django import forms
from accounts.models import User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")

    def clean_email(self):
        data = self.cleaned_data["email"]
        try:
            user_email = User.objects.get(email=data)
        except User.DoesNotExist:
            pass
        else:
            raise forms.ValidationError("Email already exist")

        return data