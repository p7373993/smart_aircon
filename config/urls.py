"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))u
"""
from django.contrib import admin
from django.urls import include, path
from sensor import views
urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('collect_power/', views.collect_power_data, name='collect_power_data'),
    path('power_usage/', views.power_usage_list, name='power_usage_list'),  
    path('power_chart/', views.power_usage_chart, name='power_usage_chart'),
    path('collect/', views.collect_data, name='collect_data'),
    path('airconlog/', views.airconlog_list, name='airconlog_list'),
    path('airconlog_chart/', views.airconlog_chart, name='airconlog_chart'),
    path('latest_airconlog/', views.latest_airconlog, name='latest_airconlog'),
    path('aircon_usage_chart/', views.aircon_usage_chart, name='aircon_usage_chart'),
    path('get_user_settings/', views.get_user_settings, name='get_user_settings'),
    path('update_user_settings/', views.update_user_settings, name='update_user_settings'), 
    path('manual_auto_control/', views.manual_auto_control, name='manual_auto_control'),

    path('control/', include('control.urls'))  
]
