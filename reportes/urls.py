from django.urls import path
from .views import reporte_ventas, exportar_ventas

app_name = "reportes"

urlpatterns = [
    path("ventas/", reporte_ventas, name="ventas"),
    path("ventas/excel/", exportar_ventas, name="exportar_ventas"),
]
