from __future__ import unicode_literals

from django import forms

from django.contrib.auth.models import User


class RegistrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        choices=kwargs.pop('choices')
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['deck'] = forms.ChoiceField(choices=choices)
        
class PasswordChangeForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username',
                      'password',
                      'first_name',
                      'last_name',
                      'email']
        
