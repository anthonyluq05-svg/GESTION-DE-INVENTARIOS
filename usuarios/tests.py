from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse


class PruebasPermisos(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        grupo_vendedor = Group.objects.create(name="Vendedor")

        grupo_almacenero = Group.objects.create(name="Almacenero")

        permisos_vendedor = Permission.objects.filter(
            content_type__app_label__in=["productos", "ventas", "inventario"],
            codename__in=[
                "view_producto",
                "view_venta",
                "add_venta",
                "change_venta",
                "view_existencia",
                "view_movimientoinventario",
            ],
        )

        grupo_vendedor.permissions.set(permisos_vendedor)

        permisos_almacenero = Permission.objects.filter(
            content_type__app_label__in=["productos", "compras", "inventario"],
            codename__in=[
                "view_producto",
                "view_compra",
                "add_compra",
                "change_compra",
                "view_existencia",
                "view_movimientoinventario",
            ],
        )

        grupo_almacenero.permissions.set(permisos_almacenero)

        cls.vendedor = User.objects.create_user(
            username="vendedor_test", password="Prueba123!Segura"
        )
        cls.vendedor.groups.add(grupo_vendedor)

        cls.almacenero = User.objects.create_user(
            username="almacenero_test", password="Prueba123!Segura"
        )
        cls.almacenero.groups.add(grupo_almacenero)

    def test_vendedor_puede_ver_ventas(self):
        self.client.force_login(self.vendedor)

        respuesta = self.client.get(reverse("ventas:lista"))

        self.assertEqual(respuesta.status_code, 200)

    def test_vendedor_no_puede_ver_compras(self):
        self.client.force_login(self.vendedor)

        respuesta = self.client.get(reverse("compras:lista"))

        self.assertEqual(respuesta.status_code, 403)

    def test_almacenero_puede_ver_compras(self):
        self.client.force_login(self.almacenero)

        respuesta = self.client.get(reverse("compras:lista"))

        self.assertEqual(respuesta.status_code, 200)

    def test_almacenero_no_puede_ver_ventas(self):
        self.client.force_login(self.almacenero)

        respuesta = self.client.get(reverse("ventas:lista"))

        self.assertEqual(respuesta.status_code, 403)

    def test_usuario_sin_sesion_es_redirigido(self):
        respuesta = self.client.get(reverse("ventas:lista"))

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/accounts/login/", respuesta.url)
