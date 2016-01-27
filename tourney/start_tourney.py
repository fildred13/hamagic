from math import ceil
from collections import Counter

from tourney.models import Match, Group, GroupStats
from tourney.tourney_functions import place, assign_byes, loser_matches_in_round, count_loser_rounds, count_rounds

def start(tourney):
    print('*****STARTING: '+tourney.name+'*****')
    
    deck_count = len(tourney.decks.all())
    print('Number of decks in tourney: '+str(deck_count))
    
    if deck_count < 4:
        tourney_status = 'Error: too few decks'
        return tourney_status
    elif deck_count > 128:
        tourney_status = 'Error: too many decks'
        return tourney_status
    elif tourney.qr_bracket == "SINGLE" and tourney.bracket == "DOUBLE" and not deck_count >= 8:
        tourney_status = 'Error: require at least 8 decks for a Single-Double Tournament'
        return tourney_status
    elif tourney.qr_bracket == "ROUND_ROBIN" and tourney.bracket == "DOUBLE" and not deck_count >= 8:
        tourney_status = 'Error: require at least 8 decks for a Round Robin-Double Tournament'
        return tourney_status
    elif tourney.qr_bracket == "ROUND_ROBIN" and tourney.bracket == "ROUND_ROBIN" and deck_count < 6:
        tourney_status = 'Error: require at least 6 decks for a Round Robin-Round Robin Tournament'
        return tourney_status
    
#DETERMINE QR BRACKET
    if tourney.qr_bracket == "SINGLE" or tourney.qr_bracket == "DOUBLE":
        if deck_count == 4:
            qr_matches = 2
            qr_loser_matches = 1
            deck_count_after_qr = 2
        elif 8 >= deck_count > 4:
            qr_matches = 4
            qr_loser_matches = 2
            deck_count_after_qr = 4
        elif 16 >= deck_count > 8:
            qr_matches = 8
            qr_loser_matches = 4
            deck_count_after_qr = 8
        elif 32 >= deck_count > 16:
            qr_matches = 16
            qr_loser_matches = 8
            deck_count_after_qr = 16
        elif 64 >= deck_count > 32:
            qr_matches = 32
            qr_loser_matches = 16
            deck_count_after_qr = 32
        elif 128 >= deck_count > 64:
            qr_matches = 64
            qr_loser_matches = 32
            deck_count_after_qr = 64
            
    if tourney.qr_bracket == "ROUND_ROBIN":
        qr_groups = int(ceil(float(deck_count) / tourney.qr_rr_group_size))   
        qr_matches_per_group = (tourney.qr_rr_group_size * (tourney.qr_rr_group_size-1)) / 2
        deck_count_after_qr = qr_groups*tourney.qr_rr_num_advance
        if tourney.bracket == "SINGLE" and deck_count_after_qr < 2:
            tourney_status = 'Error: too few decks to make bracket after round robin play'
            return tourney_status
        if tourney.bracket == "DOUBLE" and deck_count_after_qr < 4:
            tourney_status = 'Error: too few decks to make bracket after round robin play'
            return tourney_status
        
#DETERMINE BRACKET LAYOUT       
    if tourney.bracket == "SINGLE" or tourney.bracket == "DOUBLE":
        rounds = count_rounds(tourney)
        if deck_count_after_qr == 2:
            matches = 1
        elif 4 >= deck_count_after_qr > 2:
            matches = 3
        elif 8 >= deck_count_after_qr > 4:
            matches = 7
        elif 16 >= deck_count_after_qr > 8:
            matches = 15
        elif 32 >= deck_count_after_qr > 16:
            matches = 31
        elif 64 >= deck_count_after_qr > 16:
            matches = 63
        elif 128 >= deck_count_after_qr > 64:
            matches = 127
             
    if tourney.bracket == "ROUND_ROBIN":
        groups = int(ceil(float(deck_count_after_qr) / tourney.rr_group_size))   
        matches_per_group = (tourney.rr_group_size * (tourney.rr_group_size-1)) / 2
        deck_count_after_rr = groups*tourney.rr_num_advance
        if deck_count_after_rr < 2:
            tourney_status = 'Error: too few decks to make bracket after round robin play'
            return tourney_status
        rounds = count_rounds(tourney)
        if deck_count_after_rr == 2:
            matches = 1
        elif 4 >= deck_count_after_rr > 2:
            matches = 3
        elif 8 >= deck_count_after_rr > 4:
            matches = 7
        elif 16 >= deck_count_after_rr > 8:
            matches = 15
        elif 32 >= deck_count_after_rr > 16:
            matches = 31
        elif 64 >= deck_count_after_rr > 16:
            matches = 63
        elif 128 >= deck_count_after_rr > 64:
            matches = 127
        
    ############################
    ######## QR BRACKET ########
    ############################        
    if tourney.qr_bracket == "SINGLE" or tourney.qr_bracket == "DOUBLE":
        #Create QR Match Slots
        for m in range(qr_matches):
            match = Match(tourney = tourney,
                          round = 1,
                          position = m+1,
                          elimination = tourney.qr_elimination,
                          is_qualifier = True,
                          is_active = True
                          )
            match.save()
            
    if tourney.qr_bracket == "ROUND_ROBIN":
        #Create QR Match Slots
        for g in range(qr_groups):
            g = Group(tourney = tourney,
                      round = 1,
                      size = tourney.qr_rr_group_size,
                      is_active = True
                      )
            g.save()
            for m in range(int(qr_matches_per_group)):
                match = Match(tourney = tourney,
                              round = 1,
                              position = m+1,
                              group = g,
                              elimination = tourney.qr_elimination,
                              is_qualifier = True,
                              is_active = True
                              )
                match.save() 
            
    #Populate QR Match Slots
    print('Populating QR Match Slots')
    deck_list = tourney.decks.all()
    user_list = []
    for d in deck_list:
        user_list.append(d.user)
    counted_user_list = Counter(user_list)
    # The old way of organizing the user list, in case the new one breaks.  Can delete in a few versions
    # organized_user_list = sorted(counted_user_list, key=lambda u: (-counted_user_list[u], u))
    organized_user_list = sorted(counted_user_list, key=lambda u: -counted_user_list[1])
    for u in organized_user_list:
        user_deck_list = tourney.decks.filter(user=u)
        if tourney.qr_bracket == "ROUND_ROBIN":
            for d in user_deck_list:
                #hopefully pick a group where you don't already have a deck
                filtered_groups = Group.objects.filter(tourney=tourney)
                for g in filtered_groups:
                    if g.size == len(g.decks.all()):
                        filtered_groups = filtered_groups.exclude(id=g.id)
                    else:
                        for group_deck in g.decks.all():
                            if d.user == group_deck.user:
                                filtered_groups = filtered_groups.exclude(id=g.id)
                                break
                if not filtered_groups:
                    #if every group has at least one of his deck, there is nothing more we can do.
                    filtered_groups = Group.objects.filter(tourney=tourney)
                #now we know what groups would be good for this deck, so go ahead and place him in one            
                placed = False
                while placed == False:        
                    possible_group = filtered_groups.order_by('?')[:1].get()
                    if possible_group.size > len(possible_group.decks.all()):
                        gs = GroupStats(deck=d, 
                                        group=possible_group,
                                        points = 0,
                                        margin = 0)
                        gs.save()
                        placed = True
                match_count_for_deck = tourney.qr_rr_group_size-1
                empty_matches_allowed = match_count_for_deck-len(possible_group.decks.all())+1
                for i in range(match_count_for_deck):
                    place(tourney,1,False,d,possible_group,empty_matches_allowed)      
        else:
            for d in user_deck_list:
                place(tourney,1,False,d)
            
    if tourney.qr_bracket == "DOUBLE":
        #Create QR Loser Match Slots
        for m in range(qr_loser_matches):
            match = Match(tourney = tourney,
                      round = 1,
                      position = m+1,
                      elimination = tourney.qr_elimination,
                      is_qualifier = True,
                      is_active = False,
                      is_loser = True
                      )
            match.save()               
                
    ##################################
    ############  BRACKET ############
    ##################################            
    if tourney.bracket == "SINGLE" or tourney.bracket == "DOUBLE":         
        #Create Remaining Rounds Match Slots
        print("Bracket is " + str(tourney.bracket) + ". Creating Matches...")
        print("matches = " + str(matches))
        for r in range(rounds-1):
            print("r = " + str(r))
            for m in range(int(ceil(matches/(2.0**(r+1))))):
                print("m = " + str(m))
                match = Match(tourney = tourney,
                          round = r+2,
                          position = m+1,
                          elimination = tourney.elimination
                          )
                if tourney.bracket == "SINGLE":
                    if match.round == rounds:
                        match.is_final = True
                        match.elimination = tourney.final_elimination
                    if match.round == rounds-1:
                        match.is_semi = True
                        match.elimination = tourney.semi_elimination
                if tourney.bracket == "DOUBLE":
                    if match.round == rounds:
                        match.is_semi = True
                        match.elimination = tourney.semi_elimination
                match.save()
                
    if tourney.bracket == "ROUND_ROBIN":
        #Create Round Robin Round
        for g in range(groups):
            g = Group(tourney = tourney,
                      round = 2,
                      size = tourney.rr_group_size,
                      is_active = True
                      )
            g.save()
            for m in range(int(matches_per_group)):
                match = Match(tourney = tourney,
                              round = 2,
                              position = m+1,
                              group = g,
                              elimination = tourney.elimination,
                              is_active = False
                              )
                if match.round == rounds-1:
                    match.is_semi = True
                    match.elimination = tourney.semi_elimination
                match.save() 
                 
        #Create Remaining Rounds Match Slots
        for r in range(rounds-2):
            for m in range(int(ceil(matches/(2.0**(r+1))))):
                match = Match(tourney = tourney,
                          round = r+3,
                          position = m+1,
                          elimination = tourney.elimination
                          )
                if match.round == rounds:
                    match.is_final = True
                    match.elimination = tourney.final_elimination
                if match.round == rounds-1:
                    match.is_semi = True
                    match.elimination = tourney.semi_elimination
                match.save()
       
    if tourney.bracket == "DOUBLE":
        #Create Remaining Rounds Loser Match Slots
        loser_rounds = count_loser_rounds(tourney)
                
        for r in range(loser_rounds):
            this_round = r+2      
            for m in range(loser_matches_in_round(tourney.qr_bracket,
                                                  deck_count_after_qr,
                                                  this_round)
                           ):
                match = Match(tourney = tourney,
                              round = this_round,
                              position = m+1,
                              elimination = tourney.elimination,
                              is_loser = True
                              )
                if match.round == loser_rounds+1:
                    match.is_final = True
                    match.elimination = tourney.final_elimination
                if match.round == loser_rounds:
                    match.is_semi = True
                    match.elimination = tourney.semi_elimination
                match.save()
    
    ##################################
    ########### UNIVERSAL ############
    ##################################
    #after all user decks are placed, assign byes.
    assign_byes(tourney,1)
    tourney.has_started = True
    tourney.save()    
    tourney_status = 'active'                 
    return tourney_status
        
        
        
        