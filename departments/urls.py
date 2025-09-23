from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('', views.department_list, name='list'),
    path('crear/', views.department_create, name='create'),
    path('<int:pk>/', views.department_detail, name='detail'),
    path('<int:pk>/editar/', views.department_edit, name='edit'),
    path('<int:department_pk>/presupuesto/', views.department_budget_list, name='budget_list'),
    path('<int:department_pk>/presupuesto/crear/', views.department_budget_create, name='budget_create'),
    path('api/estadisticas/', views.department_stats_api, name='stats_api'),
]
