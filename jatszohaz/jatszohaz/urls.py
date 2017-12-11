from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import logout
from web import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', views.HomeView.as_view(), name="home"),
    url(r'^calendar/$', views.CalendarView.as_view(), name="calendar"),

    # User management related pages
    url(r'^profile/$', views.MyProfileView.as_view(), name="my-profile"),
    url(r'^profile/(?P<pk>\d+)/$', views.ProfileView.as_view(), name="profile"),

    # Games and renting related pages
    url(r'^games/$', views.GamesView.as_view(), name="games"),
    url(r'^new-rent/$', views.NewRentView.as_view(), name="new-rent"),
    url(r'^rent/(?P<pk>\d+)/$', views.RentView.as_view(), name="rent"),
    url(r'^my-rents/$', views.MyRentsView.as_view(), name="my-rents"),
    url(r'^rents/$', views.RentsView.as_view(), name="rents"),

    url(r'', include('social_django.urls', namespace='social')),
    url(r'^logout/', logout, {'next_page': '/'}, name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    from django.contrib.auth import views as auth_views
    urlpatterns += [url(r'^login2/$', auth_views.LoginView.as_view(template_name='login2.html'), name='login2')]
