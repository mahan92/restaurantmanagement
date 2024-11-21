from django import forms
from django.contrib.auth.models import User
from .models import UserRegistration  # Import UserRegistration if you want to use it as well


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )
    phone = forms.CharField(
        max_length=15,
        label="Phone Number",
        required=False,  # Optional field
        help_text="Optional: Phone number (max length 15)"
    )

    class Meta:
        model = User
        fields = ['username', 'email']  # Only include the default User fields

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")


        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")


        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        phone = self.cleaned_data.get('phone')
        user_registration = UserRegistration(user=user, phone=phone)
        user_registration.save()

        return user


class UserRegistrationDetailForm(forms.ModelForm):
    class Meta:
        model = UserRegistration
        fields = ['phone']
