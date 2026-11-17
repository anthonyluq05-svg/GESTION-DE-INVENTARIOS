from django.contrib import admin
from .models import Existencia, MovimientoInventario


@admin.register(Existencia)
class ExistenciaAdmin(admin.ModelAdmin):
    list_display = ("producto", "cantidad")
    search_fields = ("producto__nombre",)


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("producto", "tipo", "cantidad", "fecha", "usuario", "referencia")

    list_filter = ("tipo", "fecha")
    search_fields = ("producto__nombre",)
