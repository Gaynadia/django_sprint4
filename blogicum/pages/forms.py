from django import forms
from django.contrib.auth.models import User

from .models import FlatPage


class FlatPageForm(forms.ModelForm):
    class Meta:
        model = FlatPage
        exclude = ['created_at']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['password', 'is_staff', 'is_superuser', 'groups', 
                   'user_permissions', 'last_login', 'date_joined', 'is_active']
