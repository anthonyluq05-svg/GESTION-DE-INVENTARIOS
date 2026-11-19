from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'nombre', 'categoria', 'precio_compra',
        'precio_venta', 'stock_minimo', 'activo',
    )
    readonly_fields = ('codigo',)
    search_fields = ('codigo', 'nombre')
    list_filter = ('categoria', 'activo')
    list_editable = ('precio_venta', 'activo')
