from django.urls import path
from . import views

app_name = 'positions'

urlpatterns = [
    path('', views.position_list, name='list'),
    path('crear/', views.position_create, name='create'),
    path('<int:pk>/', views.position_detail, name='detail'),
    path('<int:pk>/editar/', views.position_edit, name='edit'),
    path('api/estadisticas/', views.position_stats_api, name='stats_api'),
]
