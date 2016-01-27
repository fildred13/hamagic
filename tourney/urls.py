from django.conf.urls import patterns, url

urlpatterns = patterns('tourney.views',
    url(r'^(?P<tourney_slug>[-\w]+)/$', 'tourney', name="tourney"),
    url(r'^(?P<tourney_slug>[-\w]+)/submit/$', 'submit_results', name="submit"),
)