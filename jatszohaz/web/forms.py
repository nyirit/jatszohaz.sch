from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from web.models import JhUser, GameGroup, Rent, GamePiece
from web.widgets import GameSelectMultiple


class JhUserForm(forms.ModelForm):
    class Meta:
        model = JhUser
        fields = ['mobile', 'room', 'email']
    email = forms.CharField(disabled=True)


class RentFormStep1(forms.Form):
    date_from = forms.DateField(
        label=_("From"),
        widget=forms.DateTimeInput(attrs={'class': "datetimepicker"}))

    date_to = forms.DateField(
        label=_("To"),
        widget=forms.DateTimeInput(attrs={'class': "datetimepicker"}))

    def clean(self):
        cleaned_data = super().clean()

        date_from = cleaned_data.get('date_from', None)
        date_to = cleaned_data.get('date_to', None)

        if date_from is not None:
            if date_from < datetime.now().date():
                self.add_error('date_from', _("Must be in the future!"))

            if date_to is not None and date_from > date_to:
                msg = _("Date from must be before date to!")
                self.add_error('date_from', msg)
                self.add_error('date_to', msg)

        return cleaned_data


class RentFormStep2(forms.Form):
    game_groups = forms.MultipleChoiceField(widget=GameSelectMultiple,
                                            required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        date_from = kwargs['initial']['date_from']
        date_to = kwargs['initial']['date_to']

        available_games = [(g.pk, g) for g in GameGroup.objects.all() if g.has_free_piece(date_from, date_to)]
        self.fields['game_groups'].choices = available_games


class RentFormStep3(forms.Form):
    comment = forms.CharField(required=False)


class NewCommentForm(forms.Form):
    comment = forms.CharField()


class EditRentForm(forms.ModelForm):
    class Meta:
        model = Rent
        fields = ['date_from', 'date_to', 'bail', ]


class AddGameForm(forms.Form):
    game = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        date_from = kwargs.pop("date_from")
        date_to = kwargs.pop("date_to")
        super().__init__(*args, **kwargs)
        available_games = [(g.pk, g) for g in GamePiece.objects.all() if g.is_free(date_from, date_to)]
        self.fields['game'].choices = available_games
