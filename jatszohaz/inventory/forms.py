from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import GameGroup
from jatszohaz.models import JhUser


class GameForm(forms.ModelForm):
    class Meta:
        model = GameGroup
        fields = ['name', 'description', 'short_description', 'image', ]

    owner = forms.ModelChoiceField(label=_("Owner"), queryset=JhUser.objects.all(), required=False)
    notes = forms.CharField(label=_("Notes"), max_length=100, required=False)
    priority = forms.IntegerField(label=_("Priority"), initial=0)
    rentable = forms.BooleanField(label=_("Rentable"), initial=True)
