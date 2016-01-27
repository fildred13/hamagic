from django import forms
from django.contrib import admin

from deck.models import Deck

class DeckAdminForm(forms.ModelForm):
    class Meta:
        model = Deck
        exclude = []

    def clean(self):
        if self.cleaned_data['type'] == 'COMMANDER' and self.cleaned_data['format'] != 'VINTAGE':
            raise forms.ValidationError('Commander is only played in vintage format.')
        return self.cleaned_data
    
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'format')
    list_filter = ['format']
    search_fields = ['format','name','user']
    readonly_fields = ("created_date", "last_update",)
    
    prepopulated_fields = {'slug' : ('name',)}
    
    fieldsets = (
                 (None, {
                         'fields':('name', 'user', 'format', 'type', 'packs', 'deck_list')
                         }),
                 ('Management', {
                                 'classes': ('collapse',),
                                 'fields':('slug', 'is_active', 'created_date', 'last_update')
                                 }),
                 ('Win/Loss Info', {
                                    'classes': ('collapse',),
                                    'fields':('game_wins', 'game_losses', 'match_wins', 'match_losses', 'tourney_semis', 'tourney_finals', 'tourney_wins', 'tourney_losses', 'tourney_bow_outs')
                                    }),
                 
                 )

admin.site.register(Deck, DeckAdmin)