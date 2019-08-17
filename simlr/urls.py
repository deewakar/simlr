from django.urls import path

from . import views

app_name = 'simlr'
urlpatterns = [
    path('', views.index, name='index'),
    path('playlist', views.playlist, name='playlist'),
    ]
