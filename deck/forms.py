from django import forms
from deck.models import Deck

class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['name', 
                  'format', 
                  'type',
                  'packs',
                  'deck_list',
                  'is_active']
        
    def clean(self):
        if self.cleaned_data['type'] == 'COMMANDER' and self.cleaned_data['format'] != 'VINTAGE':
            raise forms.ValidationError('Commander is only played in vintage format.')
        return self.cleaned_data
        