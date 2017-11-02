from django.conf.urls import url
from django.contrib import admin
from web import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', views.HomeView.as_view(), name="home"),

    # User management related pages
    url(r'^profile/$', views.MyProfileView.as_view(), name="profile"),
    url(r'^profile/$', views.ProfileView.as_view(), name="profile"),

    # Games and renting related pages
    url(r'^games/$', views.GamesView.as_view(), name="games"),

]
