from django.db import models
from django.contrib.auth.models import User


class Deck(models.Model):
    name = models.CharField(max_length=40,
                            unique=True
                            )
    slug = models.SlugField(max_length=50, 
                            unique=True, 
                            )
    user = models.ForeignKey(User)
    FORMAT_CHOICES = (
        ('MODERN', 'Modern'),
        ('STANDARD', 'Standard'),
        ('LEGACY', 'Legacy'),
        ('VINTAGE', 'Vintage'),
        ('BLOCK', 'Block')
    )
    format = models.CharField(max_length=12,
                              choices=FORMAT_CHOICES,
                              default='MODERN')
    TYPE_CHOICES = (
        ('CONSTRUCTED', 'Constructed'),
        ('DRAFT', 'Draft'),
        ('SEALED', 'Sealed'),
        ('COMMANDER', 'Commander')
    )
    type = models.CharField(max_length=12,
                            choices=TYPE_CHOICES,
                            default='CONSTRUCTED')
    packs = models.CharField(max_length=20,
                             default="Unlimited",
                             help_text='If Block, Sealed, or Draft, note the associated packs/block')
    
    deck_list = models.TextField(null=True,
                                 blank=True)
    
    match_wins = models.PositiveSmallIntegerField(default = 0)
    match_losses = models.PositiveSmallIntegerField(default = 0)
    game_wins = models.PositiveSmallIntegerField(default = 0)
    game_losses = models.PositiveSmallIntegerField(default = 0)
    tourney_semis = models.PositiveSmallIntegerField('tourney semis appearances', default = 0)
    tourney_finals = models.PositiveSmallIntegerField('tourney finals appearances', default = 0)
    tourney_wins = models.PositiveSmallIntegerField(default = 0)
    tourney_losses = models.PositiveSmallIntegerField(default = 0)
    tourney_bow_outs = models.PositiveSmallIntegerField(default = 0)
    
    is_active = models.BooleanField(default=True,
                                    help_text='Uncheck to hide deck from your All Active Decks view and Registration Selector.  Useful for "hiding" old or one-time limited decks.')
    
    created_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    
    def win_rate(self):
        if (self.match_wins +self.match_losses) > 0:
            wins = 0.0
            losses = 0.0
            wins += self.match_wins
            losses += self.match_losses
            win_rate_number = int((wins/(wins+losses))*100.0)
        else:
            win_rate_number = 0
        return win_rate_number
    
    def __str__(self):
        return self.name