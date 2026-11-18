from django.contrib import admin
from .models import Cliente, Venta, DetalleVenta


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "documento", "telefono")
    search_fields = ("nombre", "documento")


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1

    def has_add_permission(self, request, obj):
        return obj is None or obj.estado == "BORRADOR"

    def has_change_permission(self, request, obj=None):
        return obj is None or obj.estado == "BORRADOR"

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "fecha", "usuario", "estado")

    list_filter = ("estado", "fecha")
    inlines = [DetalleVentaInline]

    readonly_fields = ("estado",)

    def has_change_permission(self, request, obj=None):
        if obj and obj.estado != "BORRADOR":
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False
