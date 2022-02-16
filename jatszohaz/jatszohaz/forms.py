from django import forms
from jatszohaz.models import JhUser


class JhUserForm(forms.ModelForm):
    class Meta:
        model = JhUser
        fields = ['room', 'mobile', 'email']


class NewCommentForm(forms.Form):
    comment = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'w-100'}))
