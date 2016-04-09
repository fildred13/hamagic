from django.conf.urls import patterns, url

from tourney import views

urlpatterns = [
    url(r'^(?P<tourney_slug>[-\w]+)/$', views.tourney, name="tourney"),
    url(r'^(?P<tourney_slug>[-\w]+)/submit/$', views.submit_results, name="submit"),
]