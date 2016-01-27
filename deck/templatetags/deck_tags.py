from django.template import Library

from deck.models import Deck

register = Library()

@register.filter(name='stat')
def stat(user, stat_name):
    stat_number = 0          
    decks = Deck.objects.filter(user=user)
    for deck in decks:
        stat_number += getattr(deck, stat_name)
    return stat_number

@register.filter(name='win_rate')
def win_rate(user):
    wins = 0.0
    losses = 0.0
  
    decks = Deck.objects.filter(user=user)
    for deck in decks:
        wins += deck.match_wins
        losses += deck.match_losses
    if (wins +losses) > 0:
        win_rate_number = (wins/(wins+losses))*100.0
    else:
        win_rate_number = 0

    return int(win_rate_number)

@register.filter(name='deck_count')
def deck_count(user):
    num_user_decks = 0
    for d in Deck.objects.filter(user=user):
        num_user_decks += 1
    return int(num_user_decks)
            
        
        
    