from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    # Dashboard principal
    path('', views.forms_dashboard, name='dashboard'),
    
    # Formularios por categoría
    path('categoria/<int:category_id>/', views.forms_by_category, name='category'),
    
    # Descargar formulario
    path('descargar/<int:form_id>/', views.download_form, name='download'),
    
    # Búsqueda
    path('buscar/', views.search_forms, name='search'),
    
    # Estadísticas (solo admin)
    path('estadisticas/', views.forms_stats, name='stats'),
]
