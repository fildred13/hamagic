import random
from math import ceil

from django.utils import timezone

from tourney.models import Match, Group, GroupStats

def place(tourney,
          target_round,
          is_loser,
          deck,
          group=None,
          empty_matches_allowed=0
          ):
    match_list = Match.objects.filter(tourney=tourney,
                                      round=target_round,
                                      group=group,
                                      is_loser=is_loser)
    
    #print("Place function is placing "+str(deck)+" into target round "+str(target_round)+", is_loser="+str(is_loser))
    
    #make sure there is a spot available that isn't a self match
    allow_self_matches = False
    placeable = False
    for m in match_list:
        if m.first_deck:
            if m.second_deck:
                continue
            else:
                if m.first_deck.user != deck.user:
                    placeable = True
                    break
                else:
                    continue
        else:
            placeable = True
            break
    #since there are no valid slots, we need to see what we can do about that
    if placeable is False:
        allow_self_matches = True

    placed = False
    while placed == False:
        possible_match_position = random.randint(1,len(match_list))
        possible_match = Match.objects.get(tourney=tourney,
                                           round=target_round,
                                           group=group,
                                           is_loser=is_loser,
                                           position=possible_match_position)


        match_valid = True
        #if the target is a round robin match,
        if group is not None:
            allow_self_matches = True
            #check that this matchup isn't already created and that we arent creating too many matches vs noone (will have to add this to self-match logic)
            opposing_deck = None
            if possible_match.first_deck is not None and possible_match.second_deck is not None:
                match_valid = False
            elif possible_match.first_deck == deck or possible_match.second_deck == deck:
                match_valid = False
            elif possible_match.first_deck is not None and possible_match.second_deck is None:
                opposing_deck = possible_match.first_deck
            elif possible_match.first_deck is None and possible_match.second_deck is not None:
                opposing_deck = possible_match.second_deck
            
            empty_matches = 0
            empty_matches_allowed = empty_matches_allowed
            placeable = False    
            for m in match_list:
                if m.first_deck == deck and m.second_deck == opposing_deck:
                    if opposing_deck is None:
                        empty_matches += 1
                        if empty_matches == empty_matches_allowed:
                            match_valid = False
                            break
                    else:
                        match_valid = False
                        break
                elif m.first_deck == opposing_deck and m.second_deck == deck:
                    if opposing_deck is None:
                        empty_matches += 1
                        if empty_matches == empty_matches_allowed:
                            match_valid = False
                            break
                    else:
                        match_valid = False
                        break

        #run the self-match protection validation if allow_self_matches is false
        if match_valid:
            if allow_self_matches == False:
                if possible_match.first_deck:
                    if possible_match.first_deck.user == deck.user:
                        match_valid = False
                if possible_match.second_deck:
                    if possible_match.second_deck.user == deck.user:
                        match_valid = False
            
        #check that there is room for him in the match and, if so, assign     
        if match_valid:
            if possible_match.first_deck is None:
                possible_match.first_deck = deck
                possible_match.save()
                if possible_match.is_semi == True:
                    deck.tourney_semis += 1
                    deck.save()
                if possible_match.is_final == True:
                    deck.tourney_finals += 1
                    deck.save()
                placed = True
            elif possible_match.second_deck is None:
                possible_match.second_deck = deck
                possible_match.is_active = True
                possible_match.save()
                if possible_match.is_semi == True:
                    deck.tourney_semis += 1
                    deck.save()
                if possible_match.is_final == True:
                    deck.tourney_finals += 1
                    deck.save()
                placed = True
                
def determine_byes(tourney):
    num_rounds = count_rounds(tourney)
    
    for r in range(num_rounds):
        current_round = r+1
        next_round = r+2
        #Test that this round is even complete
        current_round_matches = Match.objects.filter(tourney=tourney,
                                                     round=current_round,
                                                     is_loser=False)
        complete_current_round_matches = Match.objects.filter(tourney=tourney,
                                                              round=current_round,
                                                              is_loser=False,
                                                              is_complete=True)
        if len(current_round_matches) == len(complete_current_round_matches):
            #Next, test that the NEXT round isn't ALREADY complete
            next_round_matches = Match.objects.filter(tourney=tourney,
                                                      round=next_round,
                                                      is_loser=False)
            complete_next_round_matches = Match.objects.filter(tourney=tourney,
                                                               round=next_round,
                                                               is_loser=False,
                                                               is_complete=True)
            if not len(next_round_matches) == len(complete_next_round_matches):
                #If there ARE incomplete matches, make sure they aren't already byes
                if not Match.objects.filter(tourney=tourney,
                                            round=next_round,
                                            is_loser=False,
                                            is_bye=True):
                    #they might just be incomplete, full matches, but then assign_byes just won't do anything
                    assign_byes(tourney,next_round)
                    
            #Since a winner's bracket round is complete, we might have a complete loser's bracket beneath.
            test_loser_bracket = False
            if current_round == 1 and tourney.qr_bracket == 'DOUBLE':
                test_loser_bracket = True    
            elif current_round > 1 and tourney.bracket == 'DOUBLE':
                test_loser_bracket = True
            if test_loser_bracket == True:
                #First, check that all the PREVIOUS loser bracket rounds are complete.
                if tourney.qr_bracket =='DOUBLE':
                    num_previous_loser_rounds = current_round-1
                else:
                    num_previous_loser_rounds = current_round-2
                previous_rounds_complete = True    
                for r in range(num_previous_loser_rounds):
                    if tourney.qr_bracket =='DOUBLE':
                        current_loser_round = r+1
                    else:
                        current_loser_round = r+2
                        
                    loser_round_matches = Match.objects.filter(tourney=tourney,
                                                               round=current_loser_round,
                                                               is_loser=True)
                    complete_loser_round_matches = Match.objects.filter(tourney=tourney,
                                                                        round=current_loser_round,
                                                                        is_loser=True,
                                                                        is_complete=True)
                    if not len(loser_round_matches) == len(complete_loser_round_matches):
                        previous_rounds_complete = False
                        break
                
                if previous_rounds_complete:
                    #See if the loser's bracket is complete
                    loser_round_matches = Match.objects.filter(tourney=tourney,
                                                               round=current_round,
                                                               is_loser=True)
                    complete_loser_round_matches = Match.objects.filter(tourney=tourney,
                                                                        round=current_round,
                                                                        is_loser=True,
                                                                        is_complete=True)
                    if not len(loser_round_matches) == len(complete_loser_round_matches):
                        #If there ARE incomplete matches, make sure they aren't already byes
                        if not Match.objects.filter(tourney=tourney,
                                                    round=current_round,
                                                    is_loser=True,
                                                    is_bye=True):
                            assign_byes(tourney,current_round,True)
                
        #if ever a primary round is incomplete, just stop.
        else:
            break                
              
def assign_byes(tourney,
                current_round,
                is_loser=False,
                ):
    for m in Match.objects.filter(tourney=tourney,round=current_round,is_loser=is_loser):
        if not m.first_deck and not m.second_deck:
            #then it is a bye-bye, so deactivate it and ignore
            m.is_bye = True
            m.is_active = False
            m.is_complete = True
            m.date_completed = timezone.now()
        elif not m.second_deck:
            m.is_bye = True
            m.is_active = False
            m.is_complete = True
            m.date_completed = timezone.now()
            is_rr = False
            target_is_rr = False
            if current_round == 2 and tourney.bracket == "ROUND_ROBIN":
                is_rr = True 
            elif current_round == 1 and tourney.qr_bracket == "ROUND_ROBIN":
                is_rr = True
            if current_round == 1 and tourney.bracket == "ROUND_ROBIN":
                target_is_rr = True 
            
            #This is unnecessary, I think, because in round robin if one deck had a bye, then ALL the decks have a bye in that group    
            if is_rr == True:
                #increment "winning" decks margin within the appropriate group
                group = m.group
                deckstats = GroupStats.objects.get(group=group, deck=m.first_deck)
                deckstats.points += 0
                deckstats.margin += 0
                if m.round == 1 and m.tourney.qr_elimination != "SINGLE":
                    deckstats.margin += 0
                elif m.is_semi and m.tourney.semi_elimination != "SINGLE":
                    deckstats.margin += 0
                elif m.is_final and m.tourney.final_elimination != "SINGLE":
                    deckstats.margin += 0    
                elif m.round > 1 and m.tourney.elimination != "SINGLE":
                    deckstats.margin += 0
                deckstats.save()
            
                
            elif tourney.bracket == "DOUBLE" and m.is_semi == True:
                final_round = Match.objects.get(tourney=tourney, is_final=True).round
                place(tourney, final_round, True, m.first_deck)
            
            elif target_is_rr == True:
                #place according to group rules
                match_count_for_deck = tourney.rr_group_size-1
                groups = Group.objects.filter(tourney=tourney, round=2)
                for g in groups:
                    if g.size == len(g.decks.all()):
                        groups = groups.exclude(id=g.id)
                    else:
                        for group_deck in g.decks.all():
                            if m.first_deck.user == group_deck.user:
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
                        gs = GroupStats(deck=m.first_deck, 
                                        group=possible_group,
                                        points = 0,
                                        margin = 0)
                        gs.save()
                        placed = True
                for i in range(match_count_for_deck):
                    empty_matches_allowed = match_count_for_deck-len(possible_group.decks.all())+1
                    place(tourney, 2, False, m.first_deck, possible_group, empty_matches_allowed)
            
            else:
                place(tourney, int(current_round+1), m.is_loser, m.first_deck)
        m.save()
    assign_group_byes(tourney,current_round)
        
def assign_group_byes(tourney,
                      current_round
                      ):
    if current_round == 1:
        nta = tourney.qr_rr_num_advance
    elif current_round > 1:
        nta = tourney.rr_num_advance
        
    for g in Group.objects.filter(tourney=tourney,round=current_round):
        if len(g.decks.all()) <= nta:
            for m in Match.objects.filter(tourney=tourney, round=current_round, group=g):
                m.is_active = False
                m.is_complete = True
                m.is_bye = True
                m.save()
            for d in g.decks.all():
                if current_round == 1 and tourney.bracket == "ROUND_ROBIN":
                    match_count_for_deck = tourney.rr_group_size-1
                    placed = False
                    while placed == False:
                        possible_group = Group.objects.filter(tourney=tourney, round=2).order_by('?')[:1].get()
                        if possible_group.size > len(possible_group.decks.all()):
                            gs = GroupStats(deck=d, 
                                            group=possible_group,
                                            points = 0,
                                            margin = 0)
                            gs.save()
                            placed = True
                    for i in range(match_count_for_deck):
                        empty_matches_allowed = match_count_for_deck-len(possible_group.decks.all())+1
                        place(tourney,current_round+1,False,d,possible_group,empty_matches_allowed)
                else:
                    place(tourney, int(current_round+1), False, d)

def count_rounds(tourney):
    deck_count = len(tourney.decks.all())
    if tourney.qr_bracket == "SINGLE" or tourney.qr_bracket == "DOUBLE":
        if deck_count == 4:
            deck_count_after_qr = 2
        elif 8 >= deck_count > 4:
            deck_count_after_qr = 4
        elif 16 >= deck_count > 8:
            deck_count_after_qr = 8
        elif 32 >= deck_count > 16:
            deck_count_after_qr = 16
        elif 64 >= deck_count > 32:
            deck_count_after_qr = 32
        elif 128 >= deck_count > 64:
            deck_count_after_qr = 64
        if tourney.bracket == "SINGLE" or tourney.bracket == "DOUBLE":
            if deck_count == 4:
                num_rounds = 2
            elif 8 >= deck_count > 4:
                num_rounds = 3
            elif 16 >= deck_count > 8:
                num_rounds = 4
            elif 32 >= deck_count > 16:
                num_rounds = 5
            elif 64 >= deck_count > 32:
                num_rounds = 6
            elif 128 >= deck_count > 64:
                num_rounds = 7
        if tourney.bracket == "ROUND_ROBIN":
            groups = int(ceil(float(deck_count_after_qr) / tourney.rr_group_size))   
            deck_count_after_rr = groups*tourney.rr_num_advance
            if deck_count_after_rr == 2:
                num_rounds = 3
            elif 4 >= deck_count_after_rr > 2:
                num_rounds = 4
            elif 8 >= deck_count_after_rr > 4:
                num_rounds = 5
            elif 16 >= deck_count_after_rr > 8:
                num_rounds = 6
            elif 32 >= deck_count_after_rr > 16:
                num_rounds = 7
            elif 64 >= deck_count_after_rr > 32:
                num_rounds = 8
            elif 128 >= deck_count_after_rr > 64:
                num_rounds = 9
            
            
    if tourney.qr_bracket == "ROUND_ROBIN":
        qr_groups = int(ceil(float(deck_count) / tourney.qr_rr_group_size))
        deck_count_after_qr = qr_groups*tourney.qr_rr_num_advance
        if tourney.bracket == "SINGLE" or tourney.bracket == "DOUBLE":
            if deck_count_after_qr == 2:
                num_rounds = 2
            elif 4 >= deck_count_after_qr > 2:
                num_rounds = 3
            elif 8 >= deck_count_after_qr > 4:
                num_rounds = 4
            elif 16 >= deck_count_after_qr > 8:
                num_rounds = 5
            elif 32 >= deck_count_after_qr > 16:
                num_rounds = 6
            elif 64 >= deck_count_after_qr > 32:
                num_rounds = 7
            elif 128 >= deck_count_after_qr > 64:
                num_rounds = 8   
        if tourney.bracket == "ROUND_ROBIN":
            groups = int(ceil(float(deck_count_after_qr) / tourney.rr_group_size))   
            deck_count_after_rr = groups*tourney.rr_num_advance
            if deck_count_after_rr == 2:
                num_rounds = 3
            elif 4 >= deck_count_after_rr > 2:
                num_rounds = 4
            elif 8 >= deck_count_after_rr > 4:
                num_rounds = 5
            elif 16 >= deck_count_after_rr > 8:
                num_rounds = 6
            elif 32 >= deck_count_after_rr > 16:
                num_rounds = 7
            elif 64 >= deck_count_after_rr > 32:
                num_rounds = 8
            elif 128 >= deck_count_after_qr > 64:
                num_rounds = 9 
            
    return num_rounds
            
def count_loser_rounds(tourney):
    deck_count = len(tourney.decks.all())
    
    if tourney.qr_bracket == "SINGLE" or tourney.qr_bracket == "DOUBLE":
        if deck_count == 4:
            deck_count_after_qr = 2
        elif 8 >= deck_count > 4:
            deck_count_after_qr = 4
        elif 16 >= deck_count > 8:
            deck_count_after_qr = 8
        elif 32 >= deck_count > 16:
            deck_count_after_qr = 16
        elif 64 >= deck_count > 32:
            deck_count_after_qr = 32
        elif 128 >= deck_count > 64:
            deck_count_after_qr = 64
            
    if tourney.qr_bracket == "ROUND_ROBIN":
        groups = ceil(float(deck_count) / tourney.qr_rr_group_size)   
        deck_count_after_qr = groups*tourney.qr_rr_num_advance
        
    if tourney.qr_bracket == "SINGLE" or tourney.qr_bracket == "ROUND_ROBIN":
        if deck_count_after_qr == 4:
            loser_rounds = 3
        elif 8 >= deck_count_after_qr > 4:
            loser_rounds = 5
        elif 16 >= deck_count_after_qr > 8:
            loser_rounds = 6
        elif 32 >= deck_count_after_qr > 16:
            loser_rounds = 8
        elif 64 >= deck_count_after_qr > 32:
            loser_rounds = 9
        elif 128 >= deck_count_after_qr > 64:
            loser_rounds = 10
    elif tourney.qr_bracket == "DOUBLE":
        if deck_count_after_qr == 2:
            loser_rounds = 2
        elif 4 >= deck_count_after_qr > 2:
            loser_rounds = 4
        elif 8 >= deck_count_after_qr > 4:
            loser_rounds = 5
        elif 16 >= deck_count_after_qr > 8:
            loser_rounds = 7
        elif 32 >= deck_count_after_qr > 16:
            loser_rounds = 8
        elif 64 >= deck_count_after_qr > 32:
            loser_rounds = 9
    return loser_rounds
            
def loser_matches_in_round(qr_bracket,
                           deck_count_after_qr,
                           this_round
                           ):
    if qr_bracket == "DOUBLE":
        if deck_count_after_qr == 2:
            if this_round == 2:
                matches_in_round = 1
            elif this_round == 3:
                matches_in_round = 1
        elif 4 >= deck_count_after_qr > 2:
            if this_round == 2:
                matches_in_round = 2
            elif this_round == 3:
                matches_in_round = 2
            elif this_round == 4:
                matches_in_round = 1
            elif this_round == 5:
                matches_in_round = 1
        elif 8 >= deck_count_after_qr > 4:
            if this_round == 2:
                matches_in_round = 4
            elif this_round == 3:
                matches_in_round = 3
            elif this_round == 4:
                matches_in_round = 2
            elif this_round == 5:
                matches_in_round = 1
            elif this_round == 6:
                matches_in_round = 1
        elif 16 >= deck_count_after_qr > 8:
            if this_round == 2:
                matches_in_round = 8
            elif this_round == 3:
                matches_in_round = 6
            elif this_round == 4:
                matches_in_round = 4
            elif this_round == 5:
                matches_in_round = 3
            elif this_round == 6:
                matches_in_round = 2
            elif this_round == 7:
                matches_in_round = 1
            elif this_round == 8:
                matches_in_round = 1
        elif 32 >= deck_count_after_qr > 16:
            if this_round == 2:
                matches_in_round = 16
            elif this_round == 3:
                matches_in_round = 12
            elif this_round == 4:
                matches_in_round = 8
            elif this_round == 5:
                matches_in_round = 5
            elif this_round == 6:
                matches_in_round = 3
            elif this_round == 7:
                matches_in_round = 2
            elif this_round == 8:
                matches_in_round = 1
            elif this_round == 9:
                matches_in_round = 1
        elif 64 >= deck_count_after_qr > 32:
            if this_round == 2:
                matches_in_round = 32
            elif this_round == 3:
                matches_in_round = 24
            elif this_round == 4:
                matches_in_round = 16
            elif this_round == 5:
                matches_in_round = 10
            elif this_round == 6:
                matches_in_round = 6
            elif this_round == 7:
                matches_in_round = 4
            elif this_round == 8:
                matches_in_round = 2
            elif this_round == 9:
                matches_in_round = 1
            elif this_round == 10:
                matches_in_round = 1
    if qr_bracket == "SINGLE" or qr_bracket == "ROUND_ROBIN":
        if deck_count_after_qr == 4:
            if this_round == 2:
                matches_in_round = 1
            elif this_round == 3:
                matches_in_round = 1
            elif this_round == 4:
                matches_in_round = 1
            else:
                matches_in_round = 0    
        elif 8 >= deck_count_after_qr > 4:
            if this_round == 2:
                matches_in_round = 2
            elif this_round == 3:
                matches_in_round = 2
            elif this_round == 4:
                matches_in_round = 2
            elif this_round == 5:
                matches_in_round = 1
            elif this_round == 6:
                matches_in_round = 1
            else:
                matches_in_round = 0   
        elif 16 >= deck_count_after_qr > 8:
            if this_round == 2:
                matches_in_round = 4
            elif this_round == 3:
                matches_in_round = 4
            elif this_round == 4:
                matches_in_round = 3
            elif this_round == 5:
                matches_in_round = 2
            elif this_round == 6:
                matches_in_round = 1
            elif this_round == 7:
                matches_in_round = 1
            else:
                matches_in_round = 0   
        elif 32 >= deck_count_after_qr > 16:
            if this_round == 2:
                matches_in_round = 8
            elif this_round == 3:
                matches_in_round = 8
            elif this_round == 4:
                matches_in_round = 6
            elif this_round == 5:
                matches_in_round = 4
            elif this_round == 6:
                matches_in_round = 3
            elif this_round == 7:
                matches_in_round = 2
            elif this_round == 8:
                matches_in_round = 1
            elif this_round == 9:
                matches_in_round = 1
            else:
                matches_in_round = 0   
        elif 64 >= deck_count_after_qr > 32:
            if this_round == 2:
                matches_in_round = 16
            elif this_round == 3:
                matches_in_round = 16
            elif this_round == 4:
                matches_in_round = 12
            elif this_round == 5:
                matches_in_round = 8
            elif this_round == 6:
                matches_in_round = 5
            elif this_round == 7:
                matches_in_round = 3
            elif this_round == 8:
                matches_in_round = 2
            elif this_round == 9:
                matches_in_round = 1
            elif this_round == 10:
                matches_in_round = 1
            else:
                matches_in_round = 0   
        elif 128 >= deck_count_after_qr > 64:
            if this_round == 2:
                matches_in_round = 32
            elif this_round == 3:
                matches_in_round = 32
            elif this_round == 4:
                matches_in_round = 24
            elif this_round == 5:
                matches_in_round = 16
            elif this_round == 6:
                matches_in_round = 10
            elif this_round == 7:
                matches_in_round = 6
            elif this_round == 8:
                matches_in_round = 4
            elif this_round == 9:
                matches_in_round = 2
            elif this_round == 10:
                matches_in_round = 1
            elif this_round == 11:
                matches_in_round = 1
            else:
                matches_in_round = 0   
    return matches_in_round
                
def test_super_entrant(tourney,
                       target_round,
                       user
                       ):
    match_list = Match.objects.filter(tourney=tourney,round=target_round)
    deck_list = []
    for m in match_list:
        deck_list.append(m.first_deck)
        deck_list.append(m.second_deck)   
    users = []
    for d in deck_list:
        if d:
            u = d.user
            users.append(u)
    if users.count(user) > len(match_list)/2:
        return True
    else:
        return False

    