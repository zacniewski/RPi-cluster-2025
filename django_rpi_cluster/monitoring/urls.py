from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('system-parameters/', views.system_parameters, name='system_parameters'),
    path('remote-script/', views.remote_script_execution, name='remote_script'),
]