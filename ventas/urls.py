from django.urls import path
from .views import (
    lista_ventas,
    crear_venta,
    confirmar_venta_view,
)

app_name = "ventas"

urlpatterns = [
    path("", lista_ventas, name="lista"),
    path("nueva/", crear_venta, name="crear"),
    path("<int:pk>/confirmar/", confirmar_venta_view, name="confirmar"),
]
