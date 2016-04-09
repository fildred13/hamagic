import string

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.template import RequestContext
from django.utils import timezone
from django.utils.text import slugify

from deck.models import Deck
from deck.forms import DeckForm
from tourney.models import Match

def deck(request, 
          template_name="deck/index.html"
          ):
    if request.method == 'POST':
        form = DeckForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            slug = slugify(name)
            user = request.user
            format = form.cleaned_data['format']
            type = form.cleaned_data['type']
            packs = form.cleaned_data['packs']
            deck_list = form.cleaned_data['deck_list']
            deck = Deck(name = name,
                        slug=slug,
                        user=user,
                        format = format,
                        type = type,
                        packs = packs,
                        deck_list = deck_list
                        )
            deck.save()
            return HttpResponseRedirect('/deck/')
    else:
        form = DeckForm()
    
    decks = Deck.objects.filter(is_active=True).order_by('-tourney_wins')
    inactive_decks = Deck.objects.filter(is_active=False).order_by('-tourney_wins')
    users = User.objects.all()
    user = request.user
    if user in users:
        username = request.user.username
        user_decks = Deck.objects.filter(user=user)
    
    return render(request,
                  template_name, 
                  locals(), 
                  context_instance=RequestContext(request))
    
    
def deck_detail(request,
                deck_slug, 
                template_name="deck/deck_detail.html"
                ):
    
    deck = Deck.objects.get(slug=deck_slug)
    users = User.objects.all()
    user = request.user
    if user in users:
        username = request.user.username
        user_decks = Deck.objects.filter(user=user)
    if deck.deck_list:
        deck_list_lines = []
        unfiltered_deck_list_lines = deck.deck_list.split('\r\n')
        for line in unfiltered_deck_list_lines:
            if not line:
                deck_list_lines.append("<li>&nbsp;</li>")
            elif line[0].isdigit():
                if line[1].isdigit():
                    card_name_search = line[3:].replace(" ","+")
                    gatherer_card_name_search = line[3:].replace(" ","+").split('+//', 1)[0]
                    new_line = '<li class="bumpin">'+line[:3]+'<a href="https://deckbox.org/mtg/'+card_name_search+'" target="_blank" data-gatherer="http://gatherer.wizards.com/pages/Card/Details.aspx?name='+gatherer_card_name_search+'" class="card_link">'+line[3:]+'</a></li>'
                    deck_list_lines.append(new_line)
                else:
                    card_name_search = line[2:].replace(" ","%20")
                    gatherer_card_name_search = line[2:].replace(" ","+").split('+//', 1)[0]
                    new_line = '<li class="bumpin">'+line[:2]+'<a href="https://deckbox.org/mtg/'+card_name_search+'" target="_blank" data-gatherer="http://gatherer.wizards.com/pages/Card/Details.aspx?name='+gatherer_card_name_search+'" class="card_link">'+line[2:]+'</a></li>'
                    deck_list_lines.append(new_line)
            elif line[:2] == "//":
                #if this is the first line, just print the comment line out
                if deck_list_lines == []:
                    deck_list_lines.append('<li>'+line+'</li>')
                #if it isn't the first line, create a new decklist
                else:
                    deck_list_lines.append('</ul><ul><li>'+line+'</li>')
            elif line == "Sideboard:":
                deck_list_lines.append('<li class="bumpin">'+line+'</li>')
    else:
        deck_list_lines = ['<li>No Deck List Yet</li>']

            
    active_tourneys =[]    
    for t in deck.tourney_set.filter(is_finished=False):
        eliminated = True
        
        #if tourney hasn't started, it hasn't been eliminated
        if t.has_started == False:
            eliminated = False
        #if deck is in any incomplete match, they are not eliminated
        if eliminated == True:
            for m in Match.objects.filter(tourney=t, is_complete=False):
                if m.first_deck:
                    if m.first_deck == deck:
                        eliminated = False
                        break
                if m.second_deck:
                    if m.second_deck == deck:
                        eliminated = False
                        break
        #if deck is in any group of a round robin which is incomplete, they are not eliminated
        if eliminated == True:
            groups = []
            if t.qr_bracket == "ROUND_ROBIN":
                for m in Match.objects.filter(tourney=t, round=1):
                    if m.first_deck:
                        if m.first_deck == deck:
                            if not m.group in groups:
                                groups.append(m.group)
                    if m.second_deck:
                        if m.second_deck == deck:
                            if not m.group in groups:
                                groups.append(m.group)    
            if t.bracket == "ROUND_ROBIN":
                for m in Match.objects.filter(tourney=t, round=2):
                    if m.first_deck:
                        if m.first_deck == deck:
                            if not m.group in groups:
                                groups.append(m.group)
                    if m.second_deck:
                        if m.second_deck == deck:
                            if not m.group in groups:
                                groups.append(m.group)
            for g in groups:
                    for m in Match.objects.filter(tourney=t, group=g):
                        if not m.is_complete:
                            eliminated = False
                            break  
        #finally, append the tournament to the list
        if eliminated == True:
            active_tourneys.append([t,'Eliminated'])
        else:
            active_tourneys.append([t,'Alive'])
                        
    past_tourneys = deck.tourney_set.filter(is_finished=True) 
    
    safe_to_change = True
    ts = deck.tourney_set.all()
    for t in ts:
        if t.is_finished:
            continue
        else:
            for m in t.match_set.all():
                if m.first_deck:
                    if m.first_deck == deck:
                        if not m.is_complete:
                            safe_to_change = False
                if m.second_deck:
                    if m.second_deck == deck:
                        if not m.is_complete:
                            safe_to_change = False
    
    if request.method == 'POST':
        old_deck_list = deck.deck_list
        form = DeckForm(request.POST, instance=deck)
        if form.is_valid():
            name = form.cleaned_data['name']
            format = form.cleaned_data['format']
            type = form.cleaned_data['type']
            packs = form.cleaned_data['packs']
            deck_list = form.cleaned_data['deck_list']
            is_active = form.cleaned_data['is_active']

            print(safe_to_change)
            print(old_deck_list)
            print(deck_list)
            if safe_to_change == False and old_deck_list != deck_list:
                send_mail('HAM: Active Deck Warning', 
                          'The deck '+deck.name+' owned by '+deck.user.username+' is active in tournaments, but had a change to its decklist.\n\nThe old decklist was:\n'+old_deck_list+'\n\nThe new decklist is:\n'+deck_list, 
                          'admin@hamagic.com', ['fildred13@gmail.com'], 
                          fail_silently=False)
            
            deck.name = name
            deck.slug = slugify(name)
            deck.format = format
            deck.type = type
            deck.packs = packs
            deck.deck_list = deck_list
            deck.is_active = is_active
            deck.last_update = timezone.now()
            
            deck.save()
            return HttpResponseRedirect('/deck/'+deck.slug+'/')
    else:
        form = DeckForm(instance=deck)       
    
    return render(request,
                  template_name, 
                  locals(), 
                  context_instance=RequestContext(request))
    
    
    
    
    
    
    
    
    
    
    
