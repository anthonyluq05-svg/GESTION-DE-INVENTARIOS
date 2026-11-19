from django.urls import path
from .depuracion import eliminar_borradores_mes, eliminar_borrador
from .views import (
    confirmar_compra_view, crear_compra, crear_proveedor,
    lista_compras, lista_proveedores, editar_proveedor, eliminar_proveedor,
)

app_name = 'compras'
urlpatterns = [
    path('', lista_compras, name='lista'),
    path('nueva/', crear_compra, name='crear'),
    path('borradores/eliminar-mes/', eliminar_borradores_mes, name='eliminar_borradores_mes'),
    path('borradores/<int:pk>/eliminar/', eliminar_borrador, name='eliminar_borrador'),
    path('<int:pk>/confirmar/', confirmar_compra_view, name='confirmar'),
    path('proveedores/', lista_proveedores, name='proveedores'),
    path('proveedores/nuevo/', crear_proveedor, name='proveedor_crear'),
    path('proveedores/<int:pk>/editar/', editar_proveedor, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', eliminar_proveedor, name='proveedor_eliminar'),
]
