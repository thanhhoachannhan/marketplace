
import logging

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core import exceptions
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger('django')

User = get_user_model()

class LoginForm(AuthenticationForm):

    error_messages = {
        'invalid_login': _('Invalid login'),
        'inactive': _('Inactive'),
    }
    
    def confirm_login_allowed(self, user):
        logger.info(f'Login failed for inactive user: {user.username}')
        if not user.is_active:
            raise exceptions.ValidationError(
                message = self.error_messages['inactive'],
                code = 'inactive',
            )


class RegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'password']

    password = forms.CharField(
        widget = forms.PasswordInput,
        label = 'Password',
    )
    confirm_password = forms.CharField(
        widget = forms.PasswordInput,
        label = 'Confirm Password',
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'fullname', 'avatar', 'address',
        ]
        widgets = {
            'address': forms.Textarea(
                attrs = {
                    'rows': 3
                },
            ),
        }


class SetNewPasswordForm(forms.Form):

    new_password = forms.CharField(
        widget = forms.PasswordInput,
        label = 'New Password',
    )

    confirm_password = forms.CharField(
        widget = forms.PasswordInput,
        label = 'Confirm Password',
    )

    def clean(self):
        cleaned_data = super().clean()
        
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data
    
