from django.conf.urls import patterns, url

from deck import views

urlpatterns = [
    url(r'^$', views.deck, name="index"),
    url(r'^(?P<deck_slug>[-\w]+)/$', views.deck_detail, name="deck_detail"),                      
]