from django.contrib import admin
from .models import Proveedor, Compra, DetalleCompra


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ruc", "telefono", "activo")
    search_fields = ("nombre", "ruc")


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("id", "proveedor", "fecha", "estado", "usuario")
    list_filter = ("estado", "fecha")
    inlines = [DetalleCompraInline]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado != "BORRADOR":
            return ("proveedor", "usuario", "estado")
        return ("estado",)

    def has_change_permission(self, request, obj=None):
        if obj and obj.estado != "BORRADOR":
            return False

        return super().has_change_permission(request, obj)
