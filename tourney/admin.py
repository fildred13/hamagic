from django import forms
from django.contrib import admin

from tourney.models import Tourney, Match, Group

class MatchInline(admin.TabularInline):
    model = Match
    extra = 1
    
class GroupInline(admin.TabularInline):
    model = Group
    extra = 1
    
class TourneyAdminForm(forms.ModelForm):
    class Meta:
        model = Tourney
        exclude = []

    def clean(self):
        if self.cleaned_data['registration_deadline'] > self.cleaned_data['start_date']:
            raise forms.ValidationError('Registration deadline must be before the start date')
        if self.cleaned_data['qr_bracket'] == "DOUBLE" and self.cleaned_data['bracket'] == "ROUND_ROBIN":
            raise forms.ValidationError('If qualifying round bracket is DOUBLE, bracket must also be DOUBLE')
        if self.cleaned_data['qr_bracket'] == "DOUBLE" and self.cleaned_data['bracket'] == "SINGLE":
            raise forms.ValidationError('If qualifying round bracket is DOUBLE, bracket must also be DOUBLE')
        if self.cleaned_data['qr_rr_num_advance'] >= self.cleaned_data['qr_rr_group_size']:
            raise forms.ValidationError('For Qualifying Round, number of advancing decks must be LESS than the group size.')
        if self.cleaned_data['rr_num_advance'] >= self.cleaned_data['rr_group_size']:
            raise forms.ValidationError('Number of advancing decks must be LESS than the group size.')
        if self.cleaned_data['rr_group_size'] > 8 or self.cleaned_data['qr_rr_group_size'] > 8:
            raise forms.ValidationError('Round Robin group sizes cannot exceed 8')
        if self.cleaned_data['rr_group_size'] < 3 or self.cleaned_data['qr_rr_group_size'] < 3:
            raise forms.ValidationError('Round Robin group sizes must be at least 3')
        if self.cleaned_data['rr_num_advance'] > 8 or self.cleaned_data['qr_rr_num_advance'] > 4:
            raise forms.ValidationError('Round Robin winners per round cannot exceed 4')
        if self.cleaned_data['type'] == 'COMMANDER' and self.cleaned_data['format'] != 'VINTAGE':
            raise forms.ValidationError('Commander is only played in vintage format.')
        return self.cleaned_data
    
class TourneyAdmin(admin.ModelAdmin):
    form = TourneyAdminForm
    
    inlines = [MatchInline, GroupInline]
    list_display = ('name', 'format', 'type', 'qr_bracket', 'bracket', 'start_date','is_finished')
    list_filter = ['is_finished']
    search_fields = ['format','type','qr_bracket', 'bracket']
    readonly_fields = ("date_created",)
    
    filter_horizontal = ['decks', 'winning_deck']
    
    prepopulated_fields = {'slug' : ('name',)}
    
    fieldsets = (
                 (None, {
                         'fields':('name', 'format', 'type', 'packs', 'qr_bracket', 'bracket', 'max_decks_per_player', 'registration_deadline', 'start_date')
                         }),
                 ('Elimination', {
                                  'fields':('qr_elimination', 'elimination', 'semi_elimination', 'final_elimination')
                                  }),
                 ('Round Robin', {
                                  'fields':('qr_rr_group_size', 'qr_rr_num_advance', 'rr_group_size', 'rr_num_advance')
                                  }),
                 ('Management', {
                                 'classes': ('collapse',),
                                 'fields':('slug', 'decks', 'date_created', 'finished_date', 'has_started', 'is_finished', 'winner', 'winning_deck')
                                 }),
                 
                 )

admin.site.register(Tourney, TourneyAdmin)