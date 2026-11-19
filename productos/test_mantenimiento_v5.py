"""Pruebas de denegación: nunca ejecutan un borrado real."""
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from mantenimiento.views import _cuenta_tecnica, restablecer_comercio


class PermisosMantenimientoTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_un_administrador_comun_no_puede_abrir_reseteo(self):
        administrador = SimpleNamespace(
            is_authenticated=True, is_active=True, is_superuser=False,
            username='administrador',
        )
        with patch.dict('os.environ', {'SGI_MAINTENANCE_USER': 'tecnico'}):
            request = self.factory.get('/productos/mantenimiento/restablecer-comercio/')
            request.user = administrador
            response = restablecer_comercio(request)
        self.assertEqual(response.status_code, 403)

    def test_superusuario_equivocado_no_es_cuenta_tecnica(self):
        usuario = SimpleNamespace(
            is_authenticated=True, is_active=True, is_superuser=True,
            username='administrador',
        )
        with patch.dict('os.environ', {'SGI_MAINTENANCE_USER': 'tecnico'}):
            self.assertFalse(_cuenta_tecnica(usuario))

    def test_cuenta_tecnica_requiere_ser_superusuario(self):
        usuario = SimpleNamespace(
            is_authenticated=True, is_active=True, is_superuser=False,
            username='tecnico',
        )
        with patch.dict('os.environ', {'SGI_MAINTENANCE_USER': 'tecnico'}):
            self.assertFalse(_cuenta_tecnica(usuario))
