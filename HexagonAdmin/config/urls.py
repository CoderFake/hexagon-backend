from django.urls import path, include
from .views import site_config_view, quick_settings_api, logout_view

app_name = 'config'

urlpatterns = [
    
    path('api/quick-settings/', quick_settings_api, name='quick_settings_api'),
    
    path('config/', site_config_view, name='site_config'),

    path('logout/', logout_view, name='logout'),
] 