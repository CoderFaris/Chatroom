from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user