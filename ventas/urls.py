from django.urls import path
from .views import lista_ventas, crear_venta, confirmar_venta_view
from .depuracion import eliminar_borradores_mes, eliminar_borrador

app_name = 'ventas'
urlpatterns = [
    path('', lista_ventas, name='lista'),
    path('nueva/', crear_venta, name='crear'),
    path('<int:pk>/confirmar/', confirmar_venta_view, name='confirmar'),
    path('borradores/eliminar-mes/', eliminar_borradores_mes, name='eliminar_borradores_mes'),
    path('borradores/<int:pk>/eliminar/', eliminar_borrador, name='eliminar_borrador'),
]
