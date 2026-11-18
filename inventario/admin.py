from django.contrib import admin
from .models import Existencia, MovimientoInventario


@admin.register(Existencia)
class ExistenciaAdmin(admin.ModelAdmin):
    list_display = ("producto", "cantidad")

    search_fields = ("producto__nombre",)

    readonly_fields = ("producto", "cantidad")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("producto", "tipo", "cantidad", "fecha", "usuario", "referencia")

    list_filter = ("tipo", "fecha")

    search_fields = ("producto__nombre",)

    readonly_fields = ("producto", "tipo", "cantidad", "fecha", "usuario", "referencia")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
