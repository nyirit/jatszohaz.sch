from django import forms
from jatszohaz.models import JhUser


class JhUserForm(forms.ModelForm):
    class Meta:
        model = JhUser
        fields = ['room', 'mobile', 'email']
