from django.conf.urls import patterns, include, url
from django.contrib import admin

import django.contrib.auth.views
import tourney.views

admin.autodiscover()

urlpatterns = [
    url(r'^$', tourney.views.index, name="home"),
    
    url(r'^deck/', include('deck.urls', namespace="deck")),
    url(r'^tourney/', include('tourney.urls', namespace="tourney")),
    url(r'^user/(?P<username>[-\w]+)/', tourney.views.user_detail, name="user_detail"),
    url(r'^past-tourneys/$', tourney.views.PastTourneyList.as_view()),
    
    url(r'^login/', django.contrib.auth.views.login, name="login"),
    url(r'^logout/', django.contrib.auth.views.logout, {'next_page': '/'}, name="logout"),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
