from django.urls import path
from mantenimiento.views import restablecer_comercio
from usuarios.views import lista_usuarios, crear_usuario, editar_usuario, eliminar_usuario
from ventas.clientes import lista_clientes, crear_cliente, editar_cliente, eliminar_cliente
from .views import (
    CategoriaCreateView, CategoriaListView, CategoriaUpdateView, CategoriaDeleteView,
    ProductoCreateView, ProductoDeleteView, ProductoListView, ProductoUpdateView,
)

app_name = 'productos'

urlpatterns = [
    path('mantenimiento/restablecer-comercio/', restablecer_comercio, name='restablecer_comercio'),
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
    path('usuarios/<int:pk>/editar/', editar_usuario, name='usuario_editar'),
    path('usuarios/<int:pk>/eliminar/', eliminar_usuario, name='usuario_eliminar'),
    path('clientes/', lista_clientes, name='clientes_lista'),
    path('clientes/nuevo/', crear_cliente, name='cliente_crear'),
    path('clientes/<int:pk>/editar/', editar_cliente, name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', eliminar_cliente, name='cliente_eliminar'),
]
