from django.urls import path
from .views import (
    lista_compras,
    crear_compra,
    confirmar_compra_view,
)

app_name = "compras"

urlpatterns = [
    path("", lista_compras, name="lista"),
    path("nueva/", crear_compra, name="crear"),
    path("<int:pk>/confirmar/", confirmar_compra_view, name="confirmar"),
]
