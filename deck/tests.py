import string
import random

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from deck.models import Deck

def _generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def _create_deck(user):
    name = 'Deck '+_generate_id()
    return Deck.objects.create(name = name,
                               slug = slugify(name),
                               format = 'MODERN',
                               type = 'CONSTRUCTED',
                               user = user)

def _create_user():
    username = 'User '+_generate_id()
    return User.objects.create(username = username, password = 'password')

class DeckTests(TestCase):

    def test_can_view_all_decks(self):
        response = self.client.get(reverse('deck:index'))
        self.assertEqual(response.status_code, 200)
        u = _create_user()
        d = _create_deck(u)
        response = self.client.get(reverse('deck:index'))
        self.assertEqual(response.status_code, 200)

    def test_can_view_deck(self):
        u = _create_user()
        d = _create_deck(u)
        response = self.client.get(reverse('deck:deck_detail', args=[d.slug]))
        self.assertEqual(response.status_code, 200)
