from django.urls import path

from . import views

app_name = 'stats'
urlpatterns = [
    path('', views.StatsView.as_view(), name="overview"),
    path('members/', views.MembersView.as_view(), name="members"),
]
