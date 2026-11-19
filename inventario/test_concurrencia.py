from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connections, close_old_connections
from django.test import TransactionTestCase, skipUnlessDBFeature

from productos.models import Categoria, Producto
from ventas.models import Venta, DetalleVenta
from ventas.services import confirmar_venta
from inventario.models import Existencia, MovimientoInventario


@skipUnlessDBFeature("has_select_for_update")
class PruebasConcurrencia(TransactionTestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username="prueba_concurrencia", password="Temporal123!Test"
        )

        categoria = Categoria.objects.create(nombre="Prueba concurrencia")

        producto = Producto.objects.create(
            codigo="CON-001",
            nombre="Producto concurrencia",
            categoria=categoria,
            precio_compra=Decimal("10.00"),
            precio_venta=Decimal("20.00"),
        )

        self.producto_id = producto.id

        Existencia.objects.create(producto=producto, cantidad=10)

        self.ventas_ids = []

        for _ in range(2):
            venta = Venta.objects.create(usuario=usuario)

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=7,
                precio_unitario=Decimal("20.00"),
            )

            self.ventas_ids.append(venta.id)

    def test_dos_ventas_simultaneas(self):
        barrera = Barrier(2)

        def procesar_venta(venta_id):
            close_old_connections()

            try:
                barrera.wait(timeout=10)
                confirmar_venta(venta_id)
                return "CONFIRMADA"
            except ValueError:
                return "RECHAZADA"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(procesar_venta, self.ventas_ids))

        existencia = Existencia.objects.get(producto_id=self.producto_id)

        self.assertEqual(resultados.count("CONFIRMADA"), 1)
        self.assertEqual(resultados.count("RECHAZADA"), 1)
        self.assertEqual(existencia.cantidad, 3)

        self.assertEqual(
            MovimientoInventario.objects.filter(
                producto_id=self.producto_id, tipo="SALIDA"
            ).count(),
            1,
        )
