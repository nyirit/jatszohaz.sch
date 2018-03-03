from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import logout
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^users/$', views.UsersView.as_view(), name="users"),
    url(r'^after-login/', views.AfterLoginView.as_view()),

    url(r'^$', views.HomeView.as_view(), name="home"),
    url(r'^calendar/$', views.CalendarView.as_view(), name="calendar"),

    # User management related pages
    url(r'^profile/$', views.MyProfileView.as_view(), name="my-profile"),
    url(r'^profile/(?P<pk>\d+)/$', views.ProfileView.as_view(), name="profile"),

    # Games and renting related pages
    url(r'^games/$', views.GamesView.as_view(), name="games"),
    url(r'', include('social_django.urls', namespace='social')),
    url(r'^logout/', logout, {'next_page': '/'}, name='logout'),

    url(r'^rent/', include('rent.urls')),
    url(r'^inventory/', include('inventory.urls')),

    url(r'^about-us/$', views.AboutUsView.as_view(), name="about-us"),
    url(r'^faq/$', views.FaqView.as_view(), name="faq"),

    url(r'^news/', include('news.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [url(r'^rosetta/', include('rosetta.urls'))]

if settings.DEBUG:
    from django.contrib.auth import views as auth_views
    urlpatterns += [url(r'^login2/$', auth_views.LoginView.as_view(template_name='login2.html'), name='login2')]
