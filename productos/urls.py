from django.urls import path
from .views import ProductoListView, ProductoCreateView, ProductoUpdateView

app_name = "productos"

urlpatterns = [
    path("", ProductoListView.as_view(), name="lista"),
    path("nuevo/", ProductoCreateView.as_view(), name="crear"),
    path("<int:pk>/editar/", ProductoUpdateView.as_view(), name="editar"),
]
