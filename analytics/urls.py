from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    path('api/analytics-data/', views.get_analytics_data, name='analytics_data'),
] 