"""
Filtros personalizados para templates de Control de Calidad
"""
from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiplica dos valores"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def get_item(dictionary, key):
    """Obtiene un item de un diccionario"""
    try:
        return dictionary.get(int(key), {})
    except (ValueError, TypeError, AttributeError):
        return {}


@register.filter
def filter_by_level(risks, level):
    """Filtra riesgos por nivel"""
    try:
        return [r for r in risks if r.risk_level == level]
    except (AttributeError, TypeError):
        return []
