from django.conf.urls import url

from . import views

app_name = 'inventory'
urlpatterns = [
    url(r'^$', views.InvListView.as_view(), name="list"),
    url(r'^(?P<game_pk>\d+)/$', views.InvListGameView.as_view(), name="list-game"),

    url(r'^new/$', views.NewInvView.as_view(), name="new"),
    url(r'^new/(?P<game_pk>\d+)/$', views.NewInvView.as_view(), name="new"),
    url(r'^edit/(?P<pk>\d+)/$', views.EditView.as_view(), name="edit"),
]
