from django import forms
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserProfile, UserProfileSettings


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.input_type = 'email'
        self.fields['password'].widget.input_type = 'password'

class RegisterFormExtended(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['bio']
    def __init__(self, *args, **kwargs):
        super(RegisterFormExtended, self).__init__(*args, **kwargs)
        self.fields['bio'].widget.input_type = 'textarea'
        self.fields['bio'].widget.attrs.update(rows="4")

class EditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class EditFormExtended(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']

class UserProfileSettingsForm(forms.ModelForm):
    notifications_follow = forms.BooleanField(help_text="we can send you a notification each time someone follows you")
    notifications_like = forms.BooleanField(help_text="we can send you a notification each time someone likes your post")
    notifications_share = forms.BooleanField(help_text="we can send you a notification each time someone shares or reacts to your post")
    notifications_tags = forms.BooleanField(help_text="we can send you a notification each time someone tags you in their post")
    notifications_message = forms.BooleanField(help_text="we can send you a notification each time someone messages you")

    notifications_to = forms.EmailField(help_text="Give us an email to send the notifications to, leave empty if you don't want to receive email notifications", required=False)

    filter_explicit = forms.BooleanField(help_text="Filter any posts tagged as explicit by our algorithms")

    class Meta:
        model = UserProfileSettings
        exclude = ['user', 'filter_tag']