"""Filtros de acceso técnico; la vista de mantenimiento valida permisos de nuevo."""
from django import template
from mantenimiento.views import _cuenta_tecnica

register = template.Library()


@register.filter(name='es_cuenta_tecnica')
def es_cuenta_tecnica(usuario):
    return _cuenta_tecnica(usuario)
