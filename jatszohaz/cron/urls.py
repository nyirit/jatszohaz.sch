from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^run/(?P<token>\w+)/$', views.Run.as_view(), name="run"),
    url(r'^run/(?P<token>\w+)/(?P<arg>\w+)/$', views.Run.as_view(), name="run"),
]
