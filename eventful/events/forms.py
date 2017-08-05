from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from crispy_forms.bootstrap import AppendedText

from .models import Event, EventInvite


class EventForm(forms.ModelForm):
    title = forms.CharField(label='Title', max_length=128)
    description = forms.CharField(label='Description', max_length=500, required=False,
                                  widget=forms.Textarea())
    start_date = forms.DateTimeField(label='Start date and time',
                                     input_formats=['%d.%m.%Y %H:%M %z'])
    privacy = forms.ChoiceField(label='Privacy', choices=Event.PRIVACY_CHOICES)
    latitude = forms.DecimalField(max_digits=10, decimal_places=7, required=False,
                                  widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=10, decimal_places=7, required=False,
                                   widget=forms.HiddenInput())

    attend = forms.BooleanField(label='Attend this event', required=False)

    def __init__(self, *args, **kwargs):
        attend = kwargs.pop('attend', None)
        super().__init__(*args, **kwargs)
        self.fields['attend'].initial = attend

    class Meta:
        model = Event
        fields = ('title', 'description', 'start_date', 'privacy', 'latitude', 'longitude')

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if self.cleaned_data.get('attend'):
            EventInvite.objects.join(event=instance, user=instance.created_by, check_perm=False)
        elif self.instance.pk:  # user is updating an event
            EventInvite.objects.self_remove(event_pk=instance.pk, user=instance.created_by)
        return instance

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_tag = False
    helper.layout = Layout(
        Field('title'),
        Field('description', rows='5', style="resize: none"),
        AppendedText('start_date', '<span class="glyphicon glyphicon-calendar"></span>'),
        Field('privacy'),
        Field('attend')
    )
