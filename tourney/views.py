from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.template import RequestContext
from django.utils import timezone
from django.views.generic import ListView

from tourney.models import Tourney, Match, GroupStats, Group
from tourney import start_tourney
from tourney.tourney_functions import place, determine_byes, count_loser_rounds, count_rounds
from deck.models import Deck
from tourney.forms import RegistrationForm, PasswordChangeForm

class PastTourneyList(ListView):
    template_name = 'tourney/past_tourney_list.html'
    queryset = Tourney.objects.filter(is_finished=True).order_by('-finished_date')

def index(request, 
          template_name="tourney/index.html"
          ):
    tourneys = Tourney.objects.filter(is_finished=False)
    past_tourneys = Tourney.objects.filter(is_finished=True).order_by('-finished_date')[:5]
    decks = Deck.objects.all().order_by('-match_wins')[:15]
    users = User.objects.all().order_by('username')
    user = request.user
    if user in users:
        username = request.user.username
        user_decks = Deck.objects.filter(user=user)
        user_matches = []
        user_tourneys = []
        for d in user_decks:
            ts = d.tourney_set.all()
            for t in ts:
                if t.is_finished:
                    continue
                else:
                    #see if there is a user match to add
                    for m in t.match_set.all():
                        if m.first_deck:
                            if m.first_deck == d:
                                if not m.is_complete:
                                    if not m in user_matches:
                                        user_matches.append(m)
                        if m.second_deck:
                            if m.second_deck == d:
                                if not m.is_complete:
                                    if not m in user_matches:
                                        user_matches.append(m)
                    #if the tourney isn't already in user_tourneys, add it
                    tourney_already_accounted = False
                    for ut in user_tourneys:
                        if ut == t:
                            tourney_already_accounted = True
                            break
                    if not tourney_already_accounted:
                        user_tourneys.append(t)
                            
    return render(request,
                  template_name, 
                  locals(), 
                  context_instance=RequestContext(request))
    
def tourney(request,
            tourney_slug,
            template_name="tourney/tourney.html"
            ):
    tourney = Tourney.objects.get(slug=tourney_slug)
    user = request.user
    logged_in = False
    if User.objects.filter(username=user.username):
        logged_in = True
    
    if tourney.is_finished:
        tourney_status = 'finished'
        
    elif tourney.has_started:
        tourney_status = 'active'
        
    elif tourney.registration_deadline > timezone.now():
        tourney_status = 'registration'
        user_decks_entered = 0
        if user.username:
            choices = []
            user_decks = user.deck_set.filter(is_active=True)
            #filter decks for format
            if tourney.format == 'STANDARD':
                user_decks = user_decks.exclude(format='MODERN')
                user_decks = user_decks.exclude(format='LEGACY')
                user_decks = user_decks.exclude(format='VINTAGE')
            elif tourney.format == 'MODERN':
                user_decks = user_decks.exclude(format='LEGACY')
                user_decks = user_decks.exclude(format='VINTAGE')
            elif tourney.format == 'LEGACY':
                user_decks = user_decks.exclude(format='VINTAGE')
            elif tourney.format == 'BLOCK':
                user_decks = user_decks.filter(format='BLOCK')
                
            #filter decks for type
            if tourney.type == 'CONSTRUCTED':
                user_decks = user_decks.exclude(type='DRAFT')
                user_decks = user_decks.exclude(type='SEALED')
            elif tourney.type == 'DRAFT':
                user_decks = user_decks.filter(type='DRAFT')
            elif tourney.type == 'SEASON':
                user_decks = user_decks.filter(type='SEASON')
            elif tourney.type == 'SEALED':
                user_decks = user_decks.filter(type='SEALED')
            elif tourney.type == 'COMMANDER':
                user_decks = user_decks.filter(type='COMMANDER')
            
            #only allow decks that aren't already in this tournament
            if user_decks:
                for d in user_decks:
                    already_registered = False
                    for rd in tourney.decks.all():
                        if rd == d:
                            already_registered = True
                            user_decks_entered += 1
                    if not already_registered:
                        choices.append((d.name,d.name))
            else:
                choices = {("no_decks","No decks!"),}
                
            decks_remaining = tourney.max_decks_per_player - user_decks_entered
                
            if request.method == 'POST':
                if 'unregister' in request.POST:
                    deck = request.POST['deck']
                    d = Deck.objects.get(name=deck)
                    tourney.decks.remove(Deck.objects.get(name=deck))
                    tourney.save()
                    messages.success(request, deck+' successfully unregistered.')
                    
                    #also, return the unbound registration form with correct info
                    decks_remaining += 1
                    choices.append((d,d.name))
                    form = RegistrationForm(choices=choices)
                else:
                    form = RegistrationForm(request.POST, choices=choices)
                    if form.is_valid():
                        deck_is_valid_submission = True
                        #Make sure they haven't submitted too many decks already
                        max_submissions = tourney.max_decks_per_player
                        user_submissions = 0
                        for d in tourney.decks.all():
                            if d.user == user:
                                user_submissions += 1
                        if user_submissions >= max_submissions:
                            messages.error(request, 'Error: You have already registered the maximum number of decks for this tournament.')
                            deck_is_valid_submission = False
                            return HttpResponseRedirect('/tourney/'+tourney.slug)
                        
                        #Make sure the deck isn't already in this tourney
                        deck = request.POST['deck']
                        if user_decks:
                            for d in user_decks:
                                if deck == d.name:
                                    for t in d.tourney_set.all():
                                        if t == tourney:
                                            messages.error(request, 'Error: '+deck+' is already registered for this tournament.')
                                            deck_is_valid_submission = False
                                            return HttpResponseRedirect('/tourney/'+tourney.slug)
                        else:
                            messages.error(request, "Error: you don't seem to have any decks.")
                            deck_is_valid_submission = False
                            return HttpResponseRedirect('/tourney/'+tourney.slug)
                        
                        #if deck is a valid submission, register it 
                        if deck_is_valid_submission:
                            print(deck)
                            tourney.decks.add(Deck.objects.get(name=deck))
                            tourney.save()
                            messages.success(request, deck+' successfully registered.')
                            
                        return HttpResponseRedirect('/tourney/'+tourney.slug)
            else:
                form = RegistrationForm(choices=choices)
                
    elif tourney.start_date < timezone.now():
        #start the tournament
        tourney_status = start_tourney.start(tourney)
    else:
        tourney_status = 'pending'
        
    if tourney.has_started:
        if tourney.bracket == "SINGLE" or tourney.bracket == "DOUBLE" or tourney.bracket == "ROUND_ROBIN":
            rounds = []
            num_groups = len(Group.objects.filter(tourney=tourney, round=2))
            deck_count = len(tourney.decks.all())
            num_rounds = count_rounds(tourney)
            for round_number in range(num_rounds):
                rn = round_number+1
                if rn <= num_rounds:
                    matches = Match.objects.filter(tourney=tourney,round=rn,is_loser=False)
                    rounds.append(matches)
                
        if tourney.bracket == "DOUBLE":
            loser_rounds = []
            num_loser_rounds = count_loser_rounds(tourney)
            r1_loser_matches = Match.objects.filter(tourney=tourney,round=1,is_loser=True)
            loser_rounds.append(r1_loser_matches)
            for round_number in range(num_loser_rounds):
                #lots of offsets because we don't add the qualifying round here
                rn = round_number+2
                if rn <= num_loser_rounds+1:
                    if num_loser_rounds+1 > rn:
                        loser_matches = Match.objects.filter(tourney=tourney,round=rn,is_loser=True)
                        loser_rounds.append(loser_matches)
                    elif num_loser_rounds+1 == rn:
                        finals_match = Match.objects.get(tourney=tourney,round=rn,is_loser=True)
                        
        if tourney.qr_bracket == "ROUND_ROBIN":
            qr_groups = Group.objects.filter(tourney=tourney, round=1)
            num_qr_groups = len(qr_groups.all())
            qr_stats = []
            for g in qr_groups:
                qr_group_decks = g.decks.order_by('-groupstats__points').order_by('-groupstats__margin')
                group_stats = []
                for d in qr_group_decks.all():
                    gs = GroupStats.objects.get(group=g, deck=d)
                    stats = (d, gs.points, gs.margin)
                    group_stats.append(stats)
                qr_stats.append(group_stats)
                
        if tourney.bracket == "ROUND_ROBIN":
            r2_groups = Group.objects.filter(tourney=tourney, round=2)
            r2_stats = []
            for g in r2_groups:
                r2_group_decks = g.decks.order_by('-groupstats__points').order_by('-groupstats__margin')
                group_stats = []
                for d in r2_group_decks.all():
                    gs = GroupStats.objects.get(group=g, deck=d)
                    stats = (d, gs.points, gs.margin)
                    group_stats.append(stats)
                r2_stats.append(group_stats)
                        
    print('Tourney status: '+tourney_status)
    if tourney_status == 'Error: too few decks':
        messages.error(request, "Error: Too Few Decks Entered in Tournament")
    elif tourney_status == 'Error: too many decks':
        messages.error(request, "Error: Too Many Decks Entered in Tournament")
    elif tourney_status == 'Error: too few decks to make Double Elimination bracket after Round Robin elimination':
        messages.error(request, tourney_status)
    elif tourney_status == 'Error: require at least 8 decks for a Single-Double Tournament':
        messages.error(request, tourney_status)
    elif tourney_status == 'Error: require at least 8 decks for a Round Robin-Double Tournament':
        messages.error(request, tourney_status)
    elif tourney_status == 'Error: too many decks to make bracket after round robin play':
        messages.error(request, tourney_status)
    elif tourney_status == 'Error: require at least 6 decks for a Round Robin-Round Robin Tournament':
        messages.error(request, tourney_status)
    elif tourney_status == 'Error: too few decks to make bracket after round robin play':
        messages.error(request, tourney_status)

    return render(request,
                  template_name, 
                  locals(), 
                  context_instance=RequestContext(request))
    
def submit_results(request,
                   tourney_slug,
                   ):
    tourney = Tourney.objects.get(slug=tourney_slug)
    #make sure they didn't leave anything blank:
    if 'first_deck_wins' in request.POST and 'second_deck_wins' in request.POST:
        try:
            first_deck_wins = int(request.POST['first_deck_wins'])
            second_deck_wins = int(request.POST['second_deck_wins'])
        #if they entered text or something, tell them they are a dingus:
        except ValueError:
            messages.error(request, 'Error: Please enter valid values for submission.') 
            return HttpResponseRedirect(reverse('tourney:tourney', args=(tourney_slug,)))
        #make sure there are no negative numbers
        if first_deck_wins < 0 or second_deck_wins < 0:
            messages.error(request, 'Error: No negative game wins allowed') 
            return HttpResponseRedirect(reverse('tourney:tourney', args=(tourney_slug,)))
        
        #MAKE SURE THE MATCH WASN'T ALREADY SUBMITTED
        match = Match.objects.get(id=request.POST['match_id'])
        if match.is_complete:
            messages.error(request, 'Error: Match results already submitted') 
            return HttpResponseRedirect(reverse('tourney:tourney', args=(tourney_slug,)))
        
        #validate that they entered the right number of wins for the elimination type
        if match.elimination == 'SINGLE':
            elim_type = 'single elimination'
            max_wins = 1
            wins_for_winner = 1
        elif match.elimination == 'BEST_THREE':
            elim_type = 'best of three'
            max_wins = 3
            wins_for_winner = 2
        elif match.elimination == 'BEST_FIVE':
            elim_type = 'best of five'
            max_wins = 5
            wins_for_winner = 3
        elif match.elimination == 'BEST_SEVEN':
            elim_type = 'best of seven'
            max_wins = 7
            wins_for_winner = 4
            
        if first_deck_wins + second_deck_wins > max_wins:
            messages.error(request, 'Error: The submitted match is '+elim_type+', yet the total games added up to more than '+str(max_wins)+'.') 
            return HttpResponseRedirect(reverse('tourney:tourney', args=(tourney_slug,)))
        elif first_deck_wins < wins_for_winner and second_deck_wins < wins_for_winner:
            messages.error(request, 'Error: The submitted match is '+elim_type+', yet neither player had at least '+str(wins_for_winner)+' wins.') 
            return HttpResponseRedirect(reverse('tourney:tourney', args=(tourney_slug,)))
        elif first_deck_wins > wins_for_winner or second_deck_wins > wins_for_winner:
            messages.error(request, 'Error: The submitted match is '+elim_type+', yet the winner had too many wins. The maximum number of game wins the winner should have is: '+str(wins_for_winner)+'.') 
            return HttpResponseRedirect(reverse('tourney:tourney', args=(tourney_slug,)))
        ##### VALIDATION COMPLETE #####
        
        
        #Start assigning all the variables and gathering neccessary data        
        #assume the simplest case
        next_round = match.round + 1
        #add caveats for double bracket semi finals
        if tourney.bracket == "DOUBLE" and match.is_semi == True:
            final_round = Match.objects.get(tourney=tourney, is_final=True).round
        
        #determine if it is a self-match
        is_self_match = False
        if match.first_deck.user == match.second_deck.user:
            is_self_match = True
             
        #determine loser round
        if not match.is_final:
            if not match.is_loser:
                if tourney.bracket == "DOUBLE":
                    loser_round = match.round
        #determine if this is a loser round
        is_loser_round = False
        if match.is_loser:
            is_loser_round = True
        
        #actually submit the match and process
        if first_deck_wins > second_deck_wins:   
            winner = match.first_deck
            loser = match.second_deck
            winners_wins = first_deck_wins
            losers_wins = second_deck_wins
            
            if not is_self_match:
                winner.game_wins += first_deck_wins
                winner.game_losses += second_deck_wins
                loser.game_wins += second_deck_wins
                loser.game_losses += first_deck_wins
        else:
            winner = match.second_deck
            loser = match.first_deck
            winners_wins = second_deck_wins
            losers_wins = first_deck_wins
            
            if not is_self_match:
                winner.game_wins += second_deck_wins
                winner.game_losses += first_deck_wins
                loser.game_wins += first_deck_wins
                loser.game_losses += second_deck_wins
        
        if not is_self_match:    
            winner.match_wins += 1
            loser.match_losses += 1
        
        winner.save()
        loser.save()
         
        #disable current match
        match.first_deck_wins = first_deck_wins
        match.second_deck_wins = second_deck_wins
        match.is_active = False
        match.is_complete = True
        match.date_completed = timezone.now()
        match.save()
        
        if match.is_final:
            winner.tourney_wins += 1
            winner.save()
            if not is_self_match:
                loser.tourney_losses += 1
                loser.save()
            if is_self_match:
                loser.tourney_bow_outs += 1
                loser.save()
            tourney.winner = winner.user
            tourney.is_finished = True
            tourney.finished_date = timezone.now()
            tourney.save()
            tourney.winning_deck.add(winner)
        else:
            #place deck/s wherever they belong
            if match.round == 1:
                bracket_type = tourney.qr_bracket
            elif match.round > 2 and tourney.bracket == "ROUND_ROBIN":
                bracket_type = "SINGLE"
            else:
                bracket_type = tourney.bracket
                    
            if bracket_type == "SINGLE":
                if match.round == 1 and tourney.bracket == "ROUND_ROBIN":
                    #place according to group rules
                    match_count_for_deck = tourney.rr_group_size-1
                    groups = Group.objects.filter(tourney=tourney, round=2)
                    for g in groups:
                        if g.size == len(g.decks.all()):
                            groups = groups.exclude(id=g.id)
                        else:
                            for group_deck in g.decks.all():
                                if winner.user == group_deck.user:
                                    groups = groups.exclude(id=g.id)
                                    break
                    if not groups:
                        #if every group has at least one of his deck, there is nothing more we can do.
                        groups = Group.objects.filter(tourney=tourney, round=2)
                    placed = False
                    while placed == False:
                        possible_group = groups.order_by('?')[:1].get()
                        placeable = False
                        if possible_group.decks:
                            if possible_group.size > len(possible_group.decks.all()):
                                placeable = True
                        elif not possible_group.decks:
                            placeable = True
                        if placeable == True:
                            gs = GroupStats(deck=winner, 
                                            group=possible_group,
                                            points = 0,
                                            margin = 0)
                            gs.save()
                            placed = True
                    for i in range(match_count_for_deck):
                        empty_matches_allowed = match_count_for_deck-len(possible_group.decks.all())+1
                        place(tourney, 2, False, winner, possible_group, empty_matches_allowed)
                else:
                    place(tourney,next_round,False,winner)
                if not is_self_match:
                    loser.tourney_losses += 1
                    loser.save()
                if is_self_match:
                    loser.tourney_bow_outs += 1
                    loser.save()
            elif bracket_type == "DOUBLE":
                if not is_loser_round:
                    if match.is_semi:
                        place(tourney,final_round,True,winner)   
                    else: 
                        place(tourney,next_round,False,winner)
                    place(tourney,loser_round,True,loser)
                if is_loser_round:
                    place(tourney,next_round,True,winner)
                    if not is_self_match:
                        loser.tourney_losses += 1
                        loser.save()
                    if is_self_match:
                        loser.tourney_bow_outs += 1
                        loser.save()
            elif bracket_type == "ROUND_ROBIN":
                #Increment winner's information in the GroupStats
                winners_stats = GroupStats.objects.get(deck=winner, group=match.group)
                winners_stats.points += 1
                winners_stats.margin += (winners_wins - losers_wins)
                winners_stats.save()
                #increment loser's margin in the GroupStats
                losers_stats = GroupStats.objects.get(deck=loser, group=match.group)
                losers_stats.margin -= (winners_wins - losers_wins)
                losers_stats.save()
                
                #Check if the round is complete and, if it is, determine the winners
                if not Match.objects.filter(tourney=tourney,
                                            round=match.round,
                                            group=match.group,
                                            is_complete=False):
                    
                    if match.round == 1:
                        num_winners = tourney.qr_rr_num_advance
                    else:
                        num_winners = tourney.rr_num_advance
                    group_winners = GroupStats.objects.filter(group=match.group).order_by('-points','-margin','?')[:num_winners]
                    match_count_for_deck = tourney.rr_group_size-1
                    for w in group_winners:
                        if match.round == 1 and tourney.bracket == "ROUND_ROBIN":
                            #hopefully pick a group where you don't already have a deck
                            groups = Group.objects.filter(tourney=tourney, round=2)
                            for g in groups:
                                if g.size == len(g.decks.all()):
                                    groups = groups.exclude(id=g.id)
                                else:
                                    for group_deck in g.decks.all():
                                        if w.deck.user == group_deck.user:
                                            groups = groups.exclude(id=g.id)
                                            break
                            if not groups:
                                #if every group has at least one of his deck, there is nothing more we can do.
                                groups = Group.objects.filter(tourney=tourney, round=2)
                            placed = False
                            while placed == False:
                                possible_group = groups.order_by('?')[:1].get()
                                placeable = False
                                if possible_group.decks:
                                    if possible_group.size > len(possible_group.decks.all()):
                                        placeable = True
                                elif not possible_group.decks:
                                    placeable = True
                                if placeable == True:
                                    gs = GroupStats(deck=w.deck, 
                                                    group=possible_group,
                                                    points = 0,
                                                    margin = 0)
                                    gs.save()
                                    placed = True
                            for i in range(match_count_for_deck):
                                empty_matches_allowed = match_count_for_deck-len(possible_group.decks.all())+1
                                place(tourney,next_round,False,w.deck,possible_group,empty_matches_allowed)
                        else:
                            place(tourney,next_round,False,w.deck)
                            
            #lastly, determine and assign byes across the tournament    
            determine_byes(tourney)
            
        
    else:
        messages.error(request, 'Error: Please enter valid values for submission.')
        return HttpResponseRedirect(reverse('tourney:tourney', args=(tourney_slug,)))
    
    return HttpResponseRedirect(reverse('tourney:tourney', 
                                        args=(tourney_slug,)))

def user_detail(request,
                username,
                template_name="tourney/user_detail.html"
                ):
    
    current_user = request.user
    user = User.objects.get(username=username)
    user_tourney_wins = Tourney.objects.filter(winner=user)
    decks = Deck.objects.filter(user=user, is_active=True).order_by('-match_wins')
    inactive_decks = Deck.objects.filter(user=user, is_active=False).order_by('-match_wins')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST, instance=user)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            
            user.username = username
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            
            user.save()
            user = User.objects.get(username=username)
            return HttpResponseRedirect('/user/'+user.username+'/')
    else:
        form = PasswordChangeForm(instance=user)
    
    return render(request,
                  template_name, 
                  locals(), 
                  context_instance=RequestContext(request))









