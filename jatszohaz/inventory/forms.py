from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import GameGroup, GamePiece
from jatszohaz.models import JhUser


class GameForm(forms.ModelForm):
    class Meta:
        model = GameGroup
        fields = ['name', 'description', 'short_description', 'image', ]

    owner = forms.ModelChoiceField(label=_("Owner"), queryset=JhUser.objects.all(), required=False)
    notes = forms.CharField(label=_("Notes"), max_length=100, required=False)
    priority = forms.IntegerField(label=_("Priority"), initial=0)
    rentable = forms.BooleanField(label=_("Rentable"), initial=True, required=False)
    buying_date = forms.DateField(
        label=_("Buying date"),
        required=False,
        widget=forms.DateTimeInput(attrs={'class': "datetimepicker"}))
    place = forms.CharField(label=_("Place"), max_length=20, required=False)
    price = forms.IntegerField(label=_("Price (Ft)"), min_value=0, initial=0)


class GamePieceForm(forms.ModelForm):
    class Meta:
        model = GamePiece
        fields = ['owner', 'game_group', 'notes', 'priority', 'rentable', 'buying_date', 'place', 'price']
        widgets = {'buying_date': forms.DateTimeInput(attrs={'class': "datetimepicker"})}
