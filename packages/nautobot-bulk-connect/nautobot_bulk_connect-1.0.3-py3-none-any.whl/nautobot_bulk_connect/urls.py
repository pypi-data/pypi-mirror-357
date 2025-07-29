from __future__ import unicode_literals

from django.urls import path

from . import views

app_name = 'nautobot_bulk_connect'
urlpatterns = [
    path(r'connect/<uuid:pk>/add/', views.ConnectView.as_view(), name='connect'),
]
