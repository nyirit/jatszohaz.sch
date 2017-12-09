from django import forms
from web.models import JhUser


class JhUserForm(forms.ModelForm):
    class Meta:
        model = JhUser
        fields = ['mobile', 'room', 'email']
    email = forms.CharField(disabled=True)
