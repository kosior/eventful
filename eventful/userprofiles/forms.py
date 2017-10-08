from django import forms

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='First name', max_length=30, required=False)
    last_name = forms.CharField(label='Last name', max_length=30, required=False)
    email = forms.EmailField(label='Email', required=False)
    website = forms.URLField(label='Website', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['email'].initial = self.instance.user.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.instance.user.first_name = self.cleaned_data.get('first_name')
        self.instance.user.last_name = self.cleaned_data.get('last_name')
        self.instance.user.email = self.cleaned_data.get('email')
        self.instance.user.save()

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'website')


class SignupForm(forms.Form):
    def signup(self, request, user):
        user.profile.timezone = request.POST.get('timezone')
        user.save()
