from django.urls import path
from usuarios.views import lista_usuarios, crear_usuario
from .views import (
    CategoriaCreateView, CategoriaListView, CategoriaUpdateView, CategoriaDeleteView,
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
    path('categorias/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', CategoriaDeleteView.as_view(), name='categoria_eliminar'),
    path('usuarios/', lista_usuarios, name='usuarios_lista'),
    path('usuarios/nuevo/', crear_usuario, name='usuario_crear'),
]
