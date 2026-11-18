from django.urls import path
from .views import (
    reporte_ventas,
    exportar_ventas,
    reporte_compras,
    exportar_compras,
    reporte_inventario,
    exportar_inventario,
)

app_name = "reportes"

urlpatterns = [
    path("ventas/", reporte_ventas, name="ventas"),
    path("ventas/excel/", exportar_ventas, name="exportar_ventas"),
    path("compras/", reporte_compras, name="compras"),
    path("compras/excel/", exportar_compras, name="exportar_compras"),
    path("inventario/", reporte_inventario, name="inventario"),
    path("inventario/excel/", exportar_inventario, name="exportar_inventario"),
]
