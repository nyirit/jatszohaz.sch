from django.conf.urls import url

from . import views

app_name = 'news'
urlpatterns = [
    url(r'^$', views.NewsView.as_view(), name='news'),
    url(r'^new/$', views.CreateNewsView.as_view(), name='create'),
    url(r'^edit/(?P<pk>\d+)/$', views.EditNewsEntryView.as_view(), name='edit'),
]
