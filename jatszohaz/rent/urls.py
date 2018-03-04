from django.conf.urls import url

from . import views

app_name = 'rent'
urlpatterns = [
    url(r'^(?P<pk>\d+)/$', views.DetailsView.as_view(), name="details"),
    url(r'^new/$', views.NewView.as_view(), name="new"),
    url(r'^edit/(?P<pk>\d+)/$', views.EditView.as_view(), name="edit"),
    url(r'^change-status/(?P<rent_pk>\d+)/(?P<status>\w+)/$', views.ChangeStatusView.as_view(), name="change-status"),
    url(r'^remove-game/(?P<rent_pk>\d+)/(?P<game_pk>\d+)/$', views.RemoveGameView.as_view(), name="remove-game"),
    url(r'^add-game/(?P<rent_pk>\d+)/$', views.AddGameView.as_view(), name="add-game"),
    url(r'^new-comment/(?P<rent_pk>\d+)/$', views.NewCommentView.as_view(), name="new-comment"),

    url(r'^rules/$', views.RentRules.as_view(), name="rules"),

    url(r'^rents/$', views.RentsView.as_view(), name="rents"),
    url(r'^rents/(?P<status>\w+)/$', views.RentsView.as_view(), name="rents"),
    url(r'^my/$', views.MyView.as_view(), name="my"),
]
