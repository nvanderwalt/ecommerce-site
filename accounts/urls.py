from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('settings/', views.account_settings, name='settings'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password/change/', views.change_password, name='change_password'),
    path('security/logs/', views.security_logs, name='security_logs'),
] 