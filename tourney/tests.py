import string
import random
import itertools

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils import timezone

from tourney.views import tourney
from tourney.models import Tourney, Match
from tourney.tourney_functions import place, count_rounds, count_loser_rounds
from deck.models import Deck

def _generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def _create_deck(user):
    name = 'Deck'+_generate_id()
    return Deck.objects.create(name = name,
                               slug = slugify(name),
                               format = 'MODERN',
                               type = 'CONSTRUCTED',
                               user = user)

def _create_user():
        username = 'User'+_generate_id()
        user = User.objects.create(username = username, password = 'password')
        user.set_password('password')
        user.save()
        return user

def _create_tourney(num_decks=16, 
                   num_users=4, 
                   format = "MODERN", 
                   type = "CONSTRUCTED",
                   qr_bracket = "SINGLE",
                   bracket = "SINGLE",
                   qr_group_size = 4,
                   group_size = 4,
                   qr_num_to_advance = 2,
                   num_to_advance = 2
                   ):
    name = 'Tourney '+_generate_id()
    users = []
    for i in range(num_users):
        u = _create_user()
        users.append(u)
    cycle = itertools.cycle(users)
    
    t = Tourney.objects.create(name = name,
                               slug = slugify(name),
                               format = format,
                               type = type,
                               qr_bracket = qr_bracket,
                               bracket = bracket,
                               qr_rr_group_size = qr_group_size,
                               rr_group_size = group_size,
                               qr_rr_num_advance = qr_num_to_advance,
                               rr_num_advance = num_to_advance,
                               registration_deadline = timezone.now(),
                               start_date = timezone.now())
    
    for i in range(num_decks):
        d = _create_deck(next(cycle))
        t.decks.add(d)
    return t

def _create_empty_tourney( format = "MODERN",
                   type = "CONSTRUCTED",
                   qr_bracket = "SINGLE",
                   bracket = "SINGLE",
                   qr_group_size = 4,
                   group_size = 4,
                   qr_num_to_advance = 2,
                   num_to_advance = 2
                   ):
    name = 'Tourney '+_generate_id()

    t = Tourney.objects.create(name = name,
                               slug = slugify(name),
                               format = format,
                               type = type,
                               qr_bracket = qr_bracket,
                               bracket = bracket,
                               qr_rr_group_size = qr_group_size,
                               rr_group_size = group_size,
                               qr_rr_num_advance = qr_num_to_advance,
                               rr_num_advance = num_to_advance,
                               registration_deadline = timezone.datetime(2100, 1, 1),
                               start_date = timezone.datetime(2100, 1, 1))
    return t
        
class HomepageTests(TestCase):

    def test_can_view_homepage_without_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

class UserTests(TestCase):

    def test_can_login(self):
        u = _create_user()
        login = self.client.login(username=u.username,
                                  password='password')
        self.assertEqual(login, True)

    def test_correct_username_for_current_user_on_user_page(self):
        """
        Test that the correct username appears in the welcome message in the top-right
        when viewing a user page as a different user. This test is in direct response to 
        a bug in which the viewed user's username was being displayed in the welcome message.
        """
        u = _create_user()
        u2 = _create_user()
        self.client.login(username=u.username,
                          password='password')
        response = self.client.get(reverse('user_detail', args=(str(u2.username),)))
        self.assertEqual(response.context['user'].username, u.username)

class RegistrationTests(TestCase):

    def test_can_register_deck(self):
        t = _create_empty_tourney()
        u = _create_user()
        d = _create_deck(u)
        self.client.login(username=u.username,
                          password='password')
        self.client.post(reverse('tourney:tourney', args=(t.slug,)), {'deck': d.name})
        rd = t.decks.all()[0]
        self.assertEqual(rd.name, d.name)
        
class TourneyTests(TestCase):        
    #####################################
    ##### BASIC TOURNAMENT CREATION #####
    #####################################    
    def test_can_start_tourney(self):
        t = _create_tourney(6,4)
        response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
        self.assertEqual(response.status_code, 200)
        
    def test_can_advance_deck(self):
        t = _create_tourney(10,4)
        self.client.get(reverse('tourney:tourney', args=(t.slug,)))
        d = t.decks.order_by('?')[0]
        place(t,2,False,d)
        response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
        self.assertEqual(response.status_code, 200)
        
    def test_can_create_lots_of_same_users_in_one_tourney(self):
        t = _create_tourney(54,2)
        response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
        self.assertEqual(response.status_code, 200)
        
        
    #########################
    ##### SINGLE-SINGLE #####
    #########################     
    def test_can_run_single_single_tourney_of_any_size(self):
        for d in range(6):
            if d == 0:
                decks = 4
            elif d == 1:
                decks = random.randint(5,8)
            elif d == 2:
                decks = random.randint(9,16)
            elif d == 3:
                decks = random.randint(17,32)
            elif d == 4:
                decks = random.randint(33,64)
            elif d == 5:
                decks = random.randint(65,128)
            
            print('Testing can run single-single tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','SINGLE','SINGLE')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_rounds = count_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id}) 
            self.assertTrue(t.winning_deck)
            
    #########################
    ##### SINGLE-DOUBLE #####
    #########################
    def test_can_create_single_double_tourney(self):
        t = _create_tourney(16,4,'MODERN','CONSTRUCTED','SINGLE','DOUBLE')
        response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
        self.assertEqual(response.status_code, 200)
    
    def test_can_create_single_double_tourney_with_final(self):
        t = _create_tourney(16,4,'MODERN','CONSTRUCTED','SINGLE','DOUBLE')
        self.client.get(reverse('tourney:tourney', args=(t.slug,)))
        f = Match.objects.get(tourney=t,is_final=True)
        self.assertTrue(f)
        
    def test_can_create_single_double_tourney_of_any_size(self):
        for decks in range(5):
            if decks == 0:
                decks = 8
            elif decks == 1:
                decks = 16
            elif decks == 2:
                decks = 32
            elif decks == 3:
                decks = 64
            elif decks == 4:
                decks = 128
            
            print('Testing can create single-double tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','SINGLE','DOUBLE')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            f = Match.objects.get(tourney=t,is_final=True)
            self.assertTrue(f)
            
    def test_can_run_single_double_tourney_of_any_size(self):
        for d in range(5):
            if d == 0:
                decks = 8
            elif d == 1:
                decks = random.randint(9,16)
            elif d == 2:
                decks = random.randint(17,32)
            elif d == 3:
                decks = random.randint(33,64)
            elif d == 4:
                decks = random.randint(65,128)
            
            print('Testing can run single-double tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','SINGLE','DOUBLE')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_loser_rounds = count_loser_rounds(t)
            num_rounds = count_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id}) 
            for r in range(num_loser_rounds):
                round_number = r+1
                if round_number > 1 and round_number <= num_loser_rounds:
                    for m in Match.objects.filter(tourney=t, round=round_number, is_loser=True, is_complete=False):
                        if m.first_deck and m.second_deck:
                            Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id}) 
            self.assertTrue(t.winning_deck)
            
    ##############################
    ##### SINGLE-ROUND ROBIN #####
    ##############################
    def test_can_run_single_round_robin_tourney_of_any_size(self):
        for d in range(6):
            if d == 0:
                decks = 4
            elif d == 1:
                decks = random.randint(5,8)
            elif d == 2:
                decks = random.randint(9,16)
            elif d == 3:
                decks = random.randint(17,32)
            elif d == 4:
                decks = random.randint(33,64)
            elif d == 5:
                decks = random.randint(65,128)
            
            print('Testing can run single-round robin tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','SINGLE','ROUND_ROBIN')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_rounds = count_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})   
            self.assertTrue(t.winning_deck)
            
    def test_can_run_single_round_robin_tourney_with_different_groups(self):
        for d in range(6):
            if d == 0:
                decks = 4
                group_size = random.randint(3,8)
                num_to_advance = 1
            elif d == 1:
                decks = random.randint(5,8)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            elif d == 2:
                decks = random.randint(9,16)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            elif d == 3:
                decks = random.randint(17,32)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            elif d == 4:
                decks = random.randint(33,64)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            elif d == 5:
                decks = random.randint(65,128)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            
            print('Testing can run single-round robin tourney of size '+str(decks))
            print('Testing Group Size '+str(group_size)+' with number of advancers '+str(num_to_advance))   
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','SINGLE','ROUND_ROBIN',4,group_size,2,num_to_advance)
            response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            if response.context['tourney_status'] == 'Error: too few decks to make bracket after round robin play':
                print('Expected failure: too few decks to make bracket after round robin play')
                self.assertEqual(response.status_code, 200)
            else:
                num_rounds = count_rounds(t)
                for r in range(num_rounds):
                    round_number = r+1
                    for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                        if m.first_deck and m.second_deck:
                            Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})   
                self.assertTrue(t.winning_deck)
    
    
    #########################
    ##### DOUBLE-DOUBLE #####
    #########################    
    def test_can_create_double_double_tourney(self):
        t = _create_tourney(16,4,'MODERN','CONSTRUCTED','DOUBLE','DOUBLE')
        response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
        self.assertEqual(response.status_code, 200)
        
    def test_can_create_double_double_tourney_with_final(self):
        t = _create_tourney(16,4,'MODERN','CONSTRUCTED','DOUBLE','DOUBLE')
        response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
        f = Match.objects.get(tourney=t,is_final=True)
        self.assertTrue(f)
        
    def test_can_create_double_double_tourney_of_any_size(self):
        for decks in range(5):
            if decks == 0:
                decks = 8
            elif decks == 1:
                decks = 16
            elif decks == 2:
                decks = 32
            elif decks == 3:
                decks = 64
            elif decks == 4:
                decks = 128
            
            print('Testing can create double-double tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','DOUBLE','DOUBLE')
            response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            f = Match.objects.get(tourney=t,is_final=True)
            self.assertTrue(f)
            
    def test_can_run_double_double_tourney_of_any_size(self):
        for d in range(5):
            if d == 0:
                decks = 8
            elif d == 1:
                decks = random.randint(9,16)
            elif d == 2:
                decks = random.randint(17,32)
            elif d == 3:
                decks = random.randint(33,64)
            elif d == 4:
                decks = random.randint(65,128)
            
            print('Testing can run double-double tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','DOUBLE','DOUBLE')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_rounds = count_rounds(t)
            num_loser_rounds = count_loser_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id}) 
            for r in range(num_loser_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=True, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})  
            self.assertTrue(t.winning_deck)
    
    ##############################
    ##### ROUND ROBIN-SINGLE #####
    ##############################
    def test_can_run_round_robin_single_tourney_of_any_size(self):
        for d in range(6):
            if d == 0:
                decks = 4
            elif d == 1:
                decks = random.randint(5,8)
            elif d == 2:
                decks = random.randint(9,16)
            elif d == 3:
                decks = random.randint(17,32)
            elif d == 4:
                decks = random.randint(33,64)
            elif d == 5:
                decks = random.randint(65,128)
            
            print('Testing can run round robin-single tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','ROUND_ROBIN','SINGLE')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_rounds = count_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})  
            self.assertTrue(t.winning_deck)
            
    def test_can_run_round_robin_single_tourney_with_different_groups(self):
        for d in range(7):
            if d == 0:
                decks = 4
                group_size = random.randint(3,8)
                num_to_advance = 1
            elif d == 1:
                decks = random.randint(5,8)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            elif d == 2:
                decks = random.randint(9,16)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            elif d == 3:
                decks = random.randint(17,32)
                group_size = random.randint(4,8)
                num_to_advance = random.randint(1,3)
            elif d == 4:
                decks = random.randint(33,64)
                group_size = random.randint(5,8)
                num_to_advance = random.randint(1,4)
            elif d == 5:
                decks = random.randint(65,128)
                group_size = random.randint(6,8)
                num_to_advance = random.randint(1,5)
            elif d == 6:
                decks = 128
                group_size = 8
                num_to_advance = 7
            
            print('Testing can run round robin-single tourney of size '+str(decks))
            print('Testing Group Size '+str(group_size)+' with number of advancers '+str(num_to_advance))   
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','ROUND_ROBIN','SINGLE',group_size,4,num_to_advance,2)
            response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            if response.context['tourney_status'] == 'Error: too few decks to make bracket after round robin play':
                print('Expected failure: too few decks to make bracket after round robin play')
                self.assertEqual(response.status_code, 200)
            elif response.context['tourney_status'] == 'Error: too many decks to make bracket after round robin play':
                print('Expected failure: too many decks to make bracket after round robin play')
                self.assertEqual(response.status_code, 200)
            else:
                num_rounds = count_rounds(t)
                for r in range(num_rounds):
                    round_number = r+1
                    for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                        if m.first_deck and m.second_deck:
                            Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})   
                self.assertTrue(t.winning_deck)
            
    def test_can_run_5_deck_rr_single_tourney(self):
            decks = 5
            print('Testing can run round robin-single tourney of size 5')    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','ROUND_ROBIN','SINGLE')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_rounds = count_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})  
            self.assertTrue(t.winning_deck)
            
    ##############################
    ##### ROUND ROBIN-DOUBLE #####
    ##############################
    def test_can_run_round_robin_double_tourney_of_any_size(self):
        for d in range(5):
            if d == 0:
                decks = 8
            elif d == 1:
                decks = random.randint(9,16)
            elif d == 2:
                decks = random.randint(17,32)
            elif d == 3:
                decks = random.randint(33,64)
            elif d == 4:
                decks = random.randint(65,128)
            
            print('Testing can run round robin-double tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','ROUND_ROBIN','DOUBLE')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_rounds = count_rounds(t)
            num_loser_rounds = count_loser_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})
            for r in range(num_loser_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=True, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})  
            self.assertTrue(t.winning_deck)
            
    def test_can_run_round_robin_double_tourney_with_different_groups(self):
        for d in range(7):
            if d == 0:
                decks = 8
                group_size = 8
                num_to_advance = 1
            elif d == 1:
                decks = random.randint(5,8)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            elif d == 2:
                decks = random.randint(9,16)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
            elif d == 3:
                decks = random.randint(17,32)
                group_size = random.randint(4,8)
                num_to_advance = random.randint(1,3)
            elif d == 4:
                decks = random.randint(33,64)
                group_size = random.randint(5,8)
                num_to_advance = random.randint(1,4)
            elif d == 5:
                decks = random.randint(65,128)
                group_size = random.randint(6,8)
                num_to_advance = random.randint(1,5)
            elif d == 6:
                decks = 128
                group_size = 8
                num_to_advance = 7
            
            print('Testing can run round robin-double tourney of size '+str(decks))
            print('Testing Group Size '+str(group_size)+' with number of advancers '+str(num_to_advance))   
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','ROUND_ROBIN','DOUBLE',group_size,4,num_to_advance,2)
            response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            if response.context['tourney_status'] == 'Error: too few decks to make bracket after round robin play':
                print('Expected failure: too few decks to make bracket after round robin play')
                self.assertEqual(response.status_code, 200)
            elif response.context['tourney_status'] == 'Error: too many decks to make bracket after round robin play':
                print('Expected failure: too many decks to make bracket after round robin play')
                self.assertEqual(response.status_code, 200)
            elif response.context['tourney_status'] == 'Error: require at least 8 decks for a Round Robin-Double Tournament':
                print('Expected failure: require at least 8 decks for a Round Robin-Double Tournament')
                self.assertEqual(response.status_code, 200)
            else:
                num_rounds = count_rounds(t)
                for r in range(num_rounds):
                    round_number = r+1
                    for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                        if m.first_deck and m.second_deck:
                            Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})   
                self.assertTrue(t.winning_deck)
            
    def test_can_run_round_robin_double_tourney_of_size_15(self):
            decks = 15
            
            print('Testing can run round robin-double tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','ROUND_ROBIN','DOUBLE',5,4,3,2)
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_rounds = count_rounds(t)
            num_loser_rounds = count_loser_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})
            for r in range(num_loser_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=True, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})  
            self.assertTrue(t.winning_deck)
            
    ###################################
    ##### ROUND ROBIN-ROUND ROBIN #####
    ###################################
    def test_can_run_round_robin_round_robin_tourney_of_any_size(self):
        for d in range(5):
            if d == 0:
                decks = random.randint(6,8)
            elif d == 1:
                decks = random.randint(9,16)
            elif d == 2:
                decks = random.randint(17,32)
            elif d == 3:
                decks = random.randint(33,64)
            elif d == 4:
                decks = random.randint(65,128)
            
            print('Testing can run round robin-round robin tourney of size '+str(decks))    
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','ROUND_ROBIN','ROUND_ROBIN')
            self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            num_rounds = count_rounds(t)
            for r in range(num_rounds):
                round_number = r+1
                for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                    if m.first_deck and m.second_deck:
                        Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})  
            self.assertTrue(t.winning_deck)
            
    def test_can_run_round_robin_round_robin_tourney_with_different_groups(self):
        for d in range(7):
            if d == 0:
                decks = 6
                qr_group_size = 8
                group_size = 8
                num_to_advance = 1
                qr_num_to_advance = 1
            elif d == 1:
                decks = random.randint(4,8)
                qr_group_size = random.randint(3,8)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
                qr_num_to_advance = random.randint(1,2)
            elif d == 2:
                decks = random.randint(9,16)
                qr_group_size = random.randint(3,8)
                group_size = random.randint(3,8)
                num_to_advance = random.randint(1,2)
                qr_num_to_advance = random.randint(1,2)
            elif d == 3:
                decks = random.randint(17,32)
                qr_group_size = random.randint(3,8)
                group_size = random.randint(4,8)
                num_to_advance = random.randint(1,3)
                qr_num_to_advance = random.randint(1,2)
            elif d == 4:
                decks = random.randint(33,64)
                qr_group_size = random.randint(3,8)
                group_size = random.randint(5,8)
                num_to_advance = random.randint(1,4)
                qr_num_to_advance = random.randint(1,2)
            elif d == 5:
                decks = random.randint(65,128)
                qr_group_size = random.randint(3,8)
                group_size = random.randint(6,8)
                num_to_advance = random.randint(1,5)
                qr_num_to_advance = random.randint(1,2)
            elif d == 6:
                decks = 128
                qr_group_size = 3
                group_size = 8
                num_to_advance = 7
                qr_num_to_advance = 1
            
            print('Testing can run round robin-round robin tourney of size '+str(decks))
            print('Testing QR Group Size '+str(qr_group_size)+' with QR number of advancers '+str(qr_num_to_advance))  
            print('Testing Group Size '+str(group_size)+' with number of advancers '+str(num_to_advance))   
            t = _create_tourney(decks,4,'MODERN','CONSTRUCTED','ROUND_ROBIN','ROUND_ROBIN',qr_group_size,group_size,qr_num_to_advance,num_to_advance)
            response = self.client.get(reverse('tourney:tourney', args=(t.slug,)))
            if response.context['tourney_status'] == 'Error: too few decks to make bracket after round robin play':
                print('Expected failure: too few decks to make bracket after round robin play')
                self.assertEqual(response.status_code, 200)
            elif response.context['tourney_status'] == 'Error: too many decks to make bracket after round robin play':
                print('Expected failure: too many decks to make bracket after round robin play')
                self.assertEqual(response.status_code, 200)
            elif response.context['tourney_status'] == 'Error: require at least 6 decks for a Round Robin-Round Robin Tournament':
                print('Expected failure: require at least 6 decks for a Round Robin-Double Tournament')
                self.assertEqual(response.status_code, 200)
            else:
                num_rounds = count_rounds(t)
                for r in range(num_rounds):
                    round_number = r+1
                    for m in Match.objects.filter(tourney=t, round=round_number, is_loser=False, is_complete=False):
                        if m.first_deck and m.second_deck:
                            Client().post('/tourney/'+t.slug+'/submit/', {'first_deck_wins': 2, 'second_deck_wins': 0, 'match_id': m.id})   
                self.assertTrue(t.winning_deck)   
        
        
        
        
        
        
        
        
        
        
        
