from django.db import models
from django.contrib.auth.models import User

from deck.models import Deck

class Tourney(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, 
                            unique=True, 
                            help_text='Unique value for tournament page URL, created from name.')
    
    FORMAT_CHOICES = (
        ('MODERN', 'Modern'),
        ('STANDARD', 'Standard'),
        ('LEGACY', 'Legacy'),
        ('VINTAGE', 'Vintage'),
        ('BLOCK', 'Block')
    )
    format = models.CharField(max_length=12,
                              choices=FORMAT_CHOICES,
                              default='MODERN',
                              )
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
    
    BRACKET_CHOICES = (
        ('SINGLE', 'Single'),
        ('DOUBLE', 'Double'),
        ('ROUND_ROBIN', 'Round Robin'),
    )
    qr_bracket = bracket = models.CharField(max_length=12,
                               choices=BRACKET_CHOICES,
                               default='SINGLE')
    bracket = models.CharField(max_length=12,
                               choices=BRACKET_CHOICES,
                               default='SINGLE',
                               help_text='If qualifying round is DOUBLE, this must also be DOUBLE.')
    
    qr_rr_group_size = models.PositiveSmallIntegerField("QR Round Robin Group Size",
                                                        default=4,
                                                        help_text='Only used if Qualifying Round Bracket is Round Robin')
    qr_rr_num_advance = models.PositiveSmallIntegerField("QR Round Robin Number of Advancers",
                                                         default=2,
                                                         help_text='Must be less than qr_rr_group_size')
    
    rr_group_size = models.PositiveSmallIntegerField("Round Robin Group Size",
                                                     default=4,
                                                     help_text='Only used if Bracket is Round Robin')
    rr_num_advance = models.PositiveSmallIntegerField("Round Robin Number of Advancers",
                                                         default=2,
                                                         help_text='Must be less than rr_group_size')
    
    ELIMINATION_CHOICES = (
        ('SINGLE', 'Single'),
        ('BEST_THREE', 'Best of Three'),
        ('BEST_FIVE', 'Best of Five'),
        ('BEST_SEVEN', 'Best of Seven'),
    )
    qr_elimination = models.CharField(max_length=12,
                                   choices=ELIMINATION_CHOICES,
                                   default='BEST_THREE')
    elimination = models.CharField(max_length=12,
                                   choices=ELIMINATION_CHOICES,
                                   default='BEST_THREE')
    semi_elimination = models.CharField(max_length=12,
                                   choices=ELIMINATION_CHOICES,
                                   default='BEST_THREE')
    final_elimination = models.CharField(max_length=12,
                                   choices=ELIMINATION_CHOICES,
                                   default='BEST_THREE')
    
    max_decks_per_player = models.PositiveSmallIntegerField(default = 1)
    decks = models.ManyToManyField(Deck,
                                   null = True,
                                   blank = True
                                   )
    
    date_created = models.DateTimeField(auto_now_add=True)
    registration_deadline = models.DateTimeField(help_text='This datetime MUST be BEFORE the start datetime')
    start_date = models.DateTimeField(help_text='All dates Eastern Standard Time!')
    
    finished_date = models.DateTimeField(null = True,
                                         blank = True
                                         )
    has_started = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    winner = models.ForeignKey(User,
                               null = True,
                               blank = True,
                               related_name="%(app_label)s_%(class)s_winner"
                               )
    winning_deck = models.ManyToManyField(Deck,
                                          null = True,
                                          blank = True,
                                          related_name="%(app_label)s_%(class)s_windeck"
                                         )
    
    def matches_remaining(self):
        matches_remaining = len(Match.objects.filter(tourney=self,is_complete=False))
        if matches_remaining == 0:
            matches_remaining = 'Not Started'
        return str(matches_remaining)
    
    def __unicode__(self):
        return self.name
 
class Group(models.Model):
    tourney = models.ForeignKey(Tourney,
                                null = True,
                                blank = True
                                )
    
    round = models.PositiveSmallIntegerField(default = 0)
    
    size = models.PositiveSmallIntegerField()
    
    decks = models.ManyToManyField(Deck,
                                   through='GroupStats',
                                   null = True,
                                   blank = True
                                   )
    
    is_active = models.BooleanField(default=False)
    
    def __unicode__(self):    
        return 'Group '+str(self.id)
    
class GroupStats(models.Model):
    deck = models.ForeignKey(Deck)
    group = models.ForeignKey(Group)
    points = models.PositiveSmallIntegerField(default = 0)
    margin = models.PositiveSmallIntegerField(default = 0)
    
class Match(models.Model):
    tourney = models.ForeignKey(Tourney)
    
    round = models.PositiveSmallIntegerField(default = 0)
    position = models.PositiveSmallIntegerField(default = 0)
    group = models.ForeignKey(Group,
                              null = True,
                              blank = True)
    
    first_deck = models.ForeignKey(Deck,
                                   null = True,
                                   blank = True,  
                                   related_name="%(app_label)s_%(class)s_first"
                                   )
    second_deck = models.ForeignKey(Deck,
                                    null = True,
                                    blank = True, 
                                    related_name="%(app_label)s_%(class)s_second"
                                    )
    ELIMINATION_CHOICES = (
        ('SINGLE', 'Single'),
        ('BEST_THREE', 'Best of Three'),
        ('BEST_FIVE', 'Best of Five'),
        ('BEST_SEVEN', 'Best of Seven'),
        )
    
    elimination = models.CharField(max_length=12,
                                   choices=ELIMINATION_CHOICES,
                                   default='BEST_THREE')
    
    is_qualifier = models.BooleanField(default=False)
    is_semi = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    
    is_loser = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=False)
    is_bye = models.BooleanField(default=False)
    
    first_deck_wins = models.PositiveSmallIntegerField(default = 0)
    second_deck_wins = models.PositiveSmallIntegerField(default = 0)
    is_complete = models.BooleanField(default=False)
    date_completed = models.DateTimeField(null = True,
                                          blank = True
                                         )
    
    def __unicode__(self):
        if self.first_deck:
            first_deck_text = self.first_deck.name
        else:
            first_deck_text = 'TBD'
            
        if self.second_deck:
            second_deck_text = self.second_deck.name
        else:
            second_deck_text = 'TBD'
            
        return first_deck_text + " v. " + second_deck_text + " in " + self.tourney.name
    
    
    
    
    
    
    
    
    
    