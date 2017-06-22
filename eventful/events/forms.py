from django import forms

from events.models import Event


class CreateEventForm(forms.ModelForm):
    title = forms.CharField(label='Title', max_length=128)
    description = forms.CharField(label='Description', max_length=500, required=False)
    start_date = forms.DateTimeField(label='Start date and time', input_formats=['%d.%m.%Y %H:%M %z'])
    privacy = forms.ChoiceField(label='Privacy', choices=Event.PRIVACY_CHOICES)

    class Meta:
        model = Event
        fields = ('title', 'description', 'start_date', 'privacy')
