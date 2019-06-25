from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from . import views
from django.views.generic import RedirectView
from jatszohaz.views import TokenLogin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^users/$', views.UsersView.as_view(), name="users"),
    url(r'^after-login/', views.AfterLoginView.as_view()),

    url(r'^$', RedirectView.as_view(pattern_name="news:news"), name="home"),
    url(r'^calendar/$', views.CalendarView.as_view(), name="calendar"),

    # User management related pages
    url(r'^profile/$', views.MyProfileView.as_view(), name="my-profile"),
    url(r'^profile/(?P<pk>\d+)/$', views.ProfileView.as_view(), name="profile"),
    url(r'^profile/toggle-group/(?P<user_pk>\d+)/(?P<group_name>\w+)/',
        views.ProfileAddRemoveGroups.as_view(), name="toggle-user-group"),

    # Games and renting related pages
    url(r'^games/$', views.GamesView.as_view(), name="games"),
    url(r'', include('social_django.urls', namespace='social')),
    url(r'^logout/', LogoutView.as_view(), name='logout'),

    url(r'^rent/', include('rent.urls')),
    url(r'^inventory/', include('inventory.urls')),

    url(r'^about-us/$', views.AboutUsView.as_view(), name="about-us"),
    url(r'^faq/$', views.FaqView.as_view(), name="faq"),
    url(r'^admin-rules/$', views.AdminRules.as_view(), name="admin-rules"),

    url(r'^news/', include('news.urls')),
    url(r'^cron/', include('cron.urls')),
    url(r'^stats/', include('stats.urls')),

    url(r'^token-login/(?P<token>.*)/$', TokenLogin.as_view(), name="token-login"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [url(r'^rosetta/', include('rosetta.urls'))]

if settings.DEBUG:
    from django.contrib.auth import views as auth_views
    urlpatterns += [url(r'^login2/$', auth_views.LoginView.as_view(template_name='login2.html'), name='login2')]
