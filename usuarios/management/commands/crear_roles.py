from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


ROLES = {
    "Administrador": [
        "view_producto",
        "add_producto",
        "change_producto",
        "view_categoria",
        "add_categoria",
        "change_categoria",
        "view_proveedor",
        "add_proveedor",
        "change_proveedor",
        "view_compra",
        "add_compra",
        "change_compra",
        "view_cliente",
        "add_cliente",
        "change_cliente",
        "view_venta",
        "add_venta",
        "change_venta",
        "view_existencia",
        "view_movimientoinventario",
    ],
    "Vendedor": [
        "view_producto",
        "view_categoria",
        "view_cliente",
        "add_cliente",
        "view_venta",
        "add_venta",
        "change_venta",
        "view_existencia",
        "view_movimientoinventario",
    ],
    "Almacenero": [
        "view_producto",
        "add_producto",
        "change_producto",
        "view_categoria",
        "add_categoria",
        "change_categoria",
        "view_proveedor",
        "add_proveedor",
        "change_proveedor",
        "view_compra",
        "add_compra",
        "change_compra",
        "view_existencia",
        "view_movimientoinventario",
    ],
}


class Command(BaseCommand):
    help = "Crear los grupos y permisos del sistema SGI"

    def handle(self, *args, **options):
        for nombre, codigos in ROLES.items():
            grupo, _ = Group.objects.get_or_create(name=nombre)

            permisos = Permission.objects.filter(codename__in=codigos)

            grupo.permissions.set(permisos)

            self.stdout.write(
                self.style.SUCCESS(f"Rol {nombre} configurado correctamente.")
            )
