from django.urls import path
from .views import (
    CategoriaCreateView, CategoriaListView,
    ProductoCreateView, ProductoDeleteView, ProductoListView, ProductoUpdateView,
)

app_name = 'productos'

urlpatterns = [
    path('', ProductoListView.as_view(), name='lista'),
    path('nuevo/', ProductoCreateView.as_view(), name='crear'),
    path('<int:pk>/editar/', ProductoUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', ProductoDeleteView.as_view(), name='eliminar'),
    path('categorias/', CategoriaListView.as_view(), name='categorias'),
    path('categorias/nueva/', CategoriaCreateView.as_view(), name='categoria_crear'),
]
