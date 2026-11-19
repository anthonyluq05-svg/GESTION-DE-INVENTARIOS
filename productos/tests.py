from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from .models import Categoria, Producto, SecuenciaProducto


class PruebasPanaderia(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Panes')
        self.administrador = get_user_model().objects.create_user(
            username='admin_sgi_test', password='Temporal123!'
        )
        grupo = Group.objects.create(name='Administrador')
        grupo.permissions.set(Permission.objects.filter(
            content_type__app_label='productos',
            codename__in=['add_producto', 'view_producto', 'delete_producto', 'view_categoria'],
        ))
        self.administrador.groups.add(grupo)

    def crear_producto(self, nombre='Pan francés'):
        return Producto.objects.create(
            nombre=nombre, categoria=self.categoria,
            precio_compra=Decimal('0.50'), precio_venta=Decimal('1.00'),
        )

    def test_codigo_automatico_consecutivo(self):
        primero = self.crear_producto()
        segundo = self.crear_producto('Pan integral')
        self.assertEqual(primero.codigo, '00001')
        self.assertEqual(segundo.codigo, '00002')

    def test_codigo_no_se_cambia_al_editar(self):
        p = self.crear_producto()
        p.codigo = '99999'
        p.nombre = 'Pan dulce'
        p.save()
        p.refresh_from_db()
        self.assertEqual(p.codigo, '00001')

    def test_limite_de_codigos(self):
        SecuenciaProducto.objects.update_or_create(
            nombre='producto', defaults={'siguiente': 10001}
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.crear_producto()

    def test_solo_admin_puede_eliminar_producto(self):
        p = self.crear_producto()
        self.client.force_login(self.administrador)
        r = self.client.post(reverse('productos:eliminar', args=[p.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Producto.objects.filter(pk=p.pk).exists())
