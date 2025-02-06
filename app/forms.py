
import logging

from django import forms
from django.contrib.auth.forms import UsernameField, ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger('app')

User = get_user_model()


class UserChangeForm(forms.ModelForm):
    """
        From django.contrib.auth.forms
    """

    class Meta:
        model = User
        fields = "__all__"
        field_classes = {"username": UsernameField}
    
    password = ReadOnlyPasswordHashField(
        label=_('PASSWORD'),
        help_text=_(
            'RAW PASSWORD NOT SAFE, YOU CAN CHANGE BY '
            '<a href=\'{}\'> FORM </a>.'
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password:
            password.help_text = password.help_text.format(
                f"../../{self.instance.pk}/password/"
            )
        user_permissions = self.fields.get("user_permissions")
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related(
                "content_type"
            )


class AuthenticationForm(forms.Form):
    """
        From django.contrib.auth.forms
    """

    username = UsernameField(
        widget = forms.TextInput(
            attrs = {'autofocus': True},
        ),
    )
    
    password = forms.CharField(
        label = _('PASSWORD'),
        strip = False,
        widget = forms.PasswordInput(
            attrs = {'autocomplete': 'current-password'},
        ),
    )

    error_messages = {
        'invalid_login': _('Invalid login'),
        'inactive': _('Inactive'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

        # Set the max length and label for the 'username' field.
        self.username_field = User._meta.get_field(User.USERNAME_FIELD)
        username_max_length = self.username_field.max_length or 254
        self.fields['username'].max_length = username_max_length
        self.fields['username'].widget.attrs['maxlength'] = username_max_length
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        logger.info(f'Login failed for inactive user: {user.username}')
        if not user.is_active:
            raise ValidationError(
                message = self.error_messages['inactive'],
                code = 'inactive',
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
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
    
