from datetime import datetime
from django import forms
from django.forms import CheckboxSelectMultiple
from django.utils.translation import ugettext_lazy as _
from web.models import JhUser, GameGroup


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

        date_from = cleaned_data['date_from']
        date_to = cleaned_data['date_to']

        if date_from < datetime.now().date():
            self.add_error('date_from', _("Must be in the future!"))

        if date_from > date_to:
            msg = _("Date from must be before date to!")
            self.add_error('date_from', msg)
            self.add_error('date_to', msg)

        return cleaned_data


class RentFormStep2(forms.Form):
    game_groups = forms.ModelMultipleChoiceField(None,
                                                 widget=CheckboxSelectMultiple,
                                                 required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['game_groups'].queryset = GameGroup.objects.all()


class RentFormStep3(forms.Form):
    comment = forms.CharField(required=False)
