from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from crispy_forms.bootstrap import AppendedText

from events.models import Event


class EventForm(forms.ModelForm):
    title = forms.CharField(label='Title', max_length=128)
    description = forms.CharField(label='Description', max_length=500, required=False, widget=forms.Textarea())
    start_date = forms.DateTimeField(label='Start date and time', input_formats=['%d.%m.%Y %H:%M %z'])
    privacy = forms.ChoiceField(label='Privacy', choices=Event.PRIVACY_CHOICES)

    class Meta:
        model = Event
        fields = ('title', 'description', 'start_date', 'privacy')

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_tag = False
    helper.layout = Layout(
        Field('title'),
        Field('description', rows='5', style="resize: none"),
        AppendedText('start_date', '<span class="glyphicon glyphicon-calendar"></span>'),
        Field('privacy')
    )
