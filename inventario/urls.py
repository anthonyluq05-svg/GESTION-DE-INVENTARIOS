from django.urls import path
from .views import lista_inventario, lista_movimientos

app_name = "inventario"

urlpatterns = [
    path("", lista_inventario, name="lista"),
    path("movimientos/", lista_movimientos, name="movimientos"),
]
