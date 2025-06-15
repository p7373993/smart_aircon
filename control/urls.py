from django.urls import path
from . import views

urlpatterns = [
    path('remote_aircon_control/', views.remote_aircon_control, name='remote_aircon_control'),
]
