from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from inventory.models import GameGroup, GamePiece
from .models import Rent
from .widgets import GameSelectMultiple


class RentFormStep1(forms.Form):
    date_from = forms.DateField(
        label=_("Rent from"),
        widget=forms.DateTimeInput(attrs={'class': "datetimepicker"})
    )

    date_to = forms.DateField(
        label=_("Rent to"),
        widget=forms.DateTimeInput(attrs={'class': "datetimepicker"})
    )

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
    game_groups = forms.MultipleChoiceField(
        widget=GameSelectMultiple,
        required=False,
        label="",
        error_messages={'invalid_choice': _('Some selected games are not available due to concurrent user rent.')})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        date_from = kwargs['initial']['date_from']
        date_to = kwargs['initial']['date_to']

        available_games = [(g.pk, g) for g
                           in GameGroup.objects.all().order_by('name') if g.has_free_piece(date_from, date_to)]
        self.fields['game_groups'].choices = available_games


class RentFormStep3(forms.Form):
    comment = forms.CharField(
        required=False,
        label=_("Rent comment"),
        help_text=_("Rent comment help"),
        widget=forms.Textarea
    )
    responsibility = forms.BooleanField(label=_("Responsibility text."), required=True)


class NewCommentForm(forms.Form):
    comment = forms.CharField(label="", widget=forms.Textarea)


class EditRentForm(forms.ModelForm):
    error_text = ""  # bit of a hack, because BaseFrom has no useful list/dict of errors

    class Meta:
        model = Rent
        fields = ['date_from', 'date_to', 'bail', ]
        widgets = {'date_from': forms.DateTimeInput(attrs={'class': "datetimepicker"}),
                   'date_to': forms.DateTimeInput(attrs={'class': "datetimepicker"})}

    def add_error(self, field, error):
        super().add_error(field, error)
        self.error_text += str(error)

    def clean(self):
        cleaned_data = super().clean()

        # check dates
        date_from = cleaned_data.get('date_from', None)
        date_to = cleaned_data.get('date_to', None)

        if date_from is not None:
            if 'date_from' in self.changed_data and date_from < datetime.now():
                self.add_error('date_from', _("Must be in the future!"))

            if date_to is not None and date_from > date_to:
                self.add_error('date_from', _("Date from must be before date to!"))

        # check game availability in new dates
        not_available_games = []
        if 'date_from' in cleaned_data and 'date_to' in cleaned_data:
            for game in self.instance.games.all():
                if not game.is_free(cleaned_data['date_from'], cleaned_data['date_to']):
                    not_available_games.append(str(game))
        if not_available_games:
            self.add_error('date_from', _("Failed to change date. Not available: %s" % ', '.join(not_available_games)))

        return cleaned_data


class AddGameForm(forms.Form):
    game = forms.ChoiceField(label=_("New game"))

    def __init__(self, *args, **kwargs):
        date_from = kwargs.pop("date_from")
        date_to = kwargs.pop("date_to")
        super().__init__(*args, **kwargs)
        available_games = [(g.pk, g) for g in GamePiece.objects.all() if g.is_free(date_from, date_to)]
        self.fields['game'].choices = available_games
