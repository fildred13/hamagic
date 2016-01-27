from django.conf.urls import patterns, url

urlpatterns = patterns('deck.views',
    url(r'^$', 'deck', name="index"),
    url(r'^(?P<deck_slug>[-\w]+)/$', 'deck_detail', name="deck_detail"),                      
)