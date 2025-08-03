from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('system-parameters/', views.system_parameters, name='system_parameters'),
    path('remote-script/', views.remote_script_execution, name='remote_script'),
    path('remote-script/queen/', views.remote_script_execution, {'machine': 'Queen'}, name='remote_script_queen'),
    path('remote-script/rook/', views.remote_script_execution, {'machine': 'Rook'}, name='remote_script_rook'),
    path('remote-script/knight/', views.remote_script_execution, {'machine': 'Knight'}, name='remote_script_knight'),
    path('remote-script/pawn/', views.remote_script_execution, {'machine': 'Pawn'}, name='remote_script_pawn'),
]
