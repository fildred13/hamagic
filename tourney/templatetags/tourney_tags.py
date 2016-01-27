from django.utils import timezone

from django.template import Library
from tourney.models import GroupStats

register = Library()

@register.filter
def get_range( value ):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
        <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
        <li>0. Do something</li>
        <li>1. Do something</li>
        <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
    """
    return range( value )

@register.filter(name='get_points')
def get_points( deck, group ):
    gs = GroupStats.objects.get(group=group, deck=deck)
    return range( gs.points )

@register.filter(name='get_margin')
def get_margin( deck, group ):
    gs = GroupStats.objects.get(group=group, deck=deck)
    return range( gs.margin )

@register.filter(name='has_passed')
def has_passed( datetime ):
    if datetime > timezone.now():
        return True