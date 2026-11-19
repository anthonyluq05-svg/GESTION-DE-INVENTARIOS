from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


ROLES = {
    'Administrador': {
        'productos': ['view_categoria', 'add_categoria', 'change_categoria', 'delete_categoria',
                      'view_producto', 'add_producto', 'change_producto', 'delete_producto'],
        'compras': ['view_proveedor', 'add_proveedor', 'change_proveedor', 'delete_proveedor',
                   'view_compra', 'add_compra', 'change_compra'],
        'ventas': ['view_cliente', 'add_cliente', 'change_cliente', 'delete_cliente',
                  'view_venta', 'add_venta', 'change_venta'],
        'inventario': ['view_existencia', 'view_movimientoinventario'],
    },
    'Vendedor': {
        'ventas': ['view_venta', 'add_venta', 'change_venta',
                  'view_cliente', 'add_cliente'],
        'inventario': ['view_existencia', 'view_movimientoinventario'],
    },
}


class Command(BaseCommand):
    help = 'Sincroniza los roles Administrador y Vendedor del SGI.'

    def handle(self, *args, **options):
        for nombre, apps in ROLES.items():
            grupo, _ = Group.objects.get_or_create(name=nombre)
            permisos = []
            for app_label, codigos in apps.items():
                permisos.extend(Permission.objects.filter(
                    content_type__app_label=app_label, codename__in=codigos
                ))
            grupo.permissions.set(permisos)
            self.stdout.write(self.style.SUCCESS(f'Rol {nombre}: actualizado'))

        # Ya no existe este cargo. Los usuarios anteriormente asignados quedan sin él.
        Group.objects.filter(name='Almacenero').delete()
        self.stdout.write(self.style.SUCCESS('Grupo Almacenero eliminado, si existía.'))
