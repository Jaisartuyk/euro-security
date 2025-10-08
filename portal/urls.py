"""
URLs para el Portal de Aplicaciones
"""
from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.apps_portal, name='apps'),
]
