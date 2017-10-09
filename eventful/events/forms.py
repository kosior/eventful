from crispy_forms.bootstrap import AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms

from common.validators import validate_start_date
from .models import Event, EventInvite


class InviteField(forms.MultipleChoiceField):
    def valid_value(self, value):
        return True


class EventForm(forms.ModelForm):
    title = forms.CharField(label='Title', max_length=128)
    description = forms.CharField(label='Description (markdown supported)', max_length=500, required=False,
                                  widget=forms.Textarea())
    start_date = forms.DateTimeField(label='Start date and time', input_formats=['%d.%m.%Y %H:%M %z'],
                                     validators=[validate_start_date])
    privacy = forms.ChoiceField(label='Privacy', choices=Event.PRIVACY_CHOICES)
    latitude = forms.DecimalField(max_digits=10, decimal_places=7, required=False, widget=forms.HiddenInput())
    longitude = forms.DecimalField(max_digits=10, decimal_places=7, required=False, widget=forms.HiddenInput())
    attend = forms.BooleanField(label='Attend this event', required=False)
    invite = InviteField(label='Invite friends', required=False)

    def __init__(self, *args, **kwargs):
        self.attend_init = kwargs.pop('attend_init', None)
        update = kwargs.pop('update', None)
        super().__init__(*args, **kwargs)
        self.fields['attend'].initial = self.attend_init
        if update:
            del self.fields['invite']

    class Meta:
        model = Event
        fields = ('title', 'description', 'start_date', 'privacy', 'latitude', 'longitude')

    def save(self, commit=True):
        instance = super().save(commit=commit)

        user_pks_to_invite = self.cleaned_data.get('invite')
        attend = self.cleaned_data.get('attend')

        if user_pks_to_invite:
            EventInvite.objects.invite(event=instance, user=instance.created_by, pk_or_pks=user_pks_to_invite)

        if self.attend_init is False and attend:
            EventInvite.objects.join(event=instance, user=instance.created_by, check_perm=False)
        elif self.instance.pk and self.attend_init and attend is False:  # user is updating an event
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
        Field('invite', size='1'),
        Field('attend'),
    )
