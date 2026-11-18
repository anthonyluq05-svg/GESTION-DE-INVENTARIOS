from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from productos.models import Categoria, Producto
from compras.models import Proveedor, Compra, DetalleCompra
from compras.services import confirmar_compra
from ventas.models import Venta, DetalleVenta
from ventas.services import confirmar_venta
from inventario.models import Existencia, MovimientoInventario
from django.core.exceptions import ValidationError


class PruebasInventario(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="usuario_prueba", password="Test12345!Segura"
        )

        categoria = Categoria.objects.create(nombre="Categoría de prueba")

        self.producto = Producto.objects.create(
            codigo="TEST-001",
            nombre="Producto de prueba",
            categoria=categoria,
            precio_compra=Decimal("10.00"),
            precio_venta=Decimal("20.00"),
        )

        self.proveedor = Proveedor.objects.create(nombre="Proveedor de prueba")

    def crear_compra(self):
        compra = Compra.objects.create(proveedor=self.proveedor, usuario=self.usuario)

        DetalleCompra.objects.create(
            compra=compra,
            producto=self.producto,
            cantidad=10,
            costo_unitario=Decimal("10.00"),
        )

        return compra

    # PRUEBA 1: Una compra aumenta el stock
    def test_compra_actualiza_stock(self):
        compra = self.crear_compra()

        confirmar_compra(compra.id)

        existencia = Existencia.objects.get(producto=self.producto)

        self.assertEqual(existencia.cantidad, 10)

    # PRUEBA 2: Una compra no se confirma dos veces
    def test_compra_no_se_confirma_dos_veces(self):
        compra = self.crear_compra()

        confirmar_compra(compra.id)

        with self.assertRaises(ValueError):
            confirmar_compra(compra.id)

        existencia = Existencia.objects.get(producto=self.producto)

        self.assertEqual(existencia.cantidad, 10)

    # PRUEBA 3: Una venta descuenta el stock
    def test_venta_descuenta_stock(self):
        compra = self.crear_compra()
        confirmar_compra(compra.id)

        venta = Venta.objects.create(usuario=self.usuario)

        DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=3,
            precio_unitario=Decimal("20.00"),
        )

        confirmar_venta(venta.id)

        existencia = Existencia.objects.get(producto=self.producto)

        self.assertEqual(existencia.cantidad, 7)

    # PRUEBA 4: No permite vender sin stock
    def test_venta_sin_stock(self):
        venta = Venta.objects.create(usuario=self.usuario)

        DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=5,
            precio_unitario=Decimal("20.00"),
        )

        with self.assertRaises(ValueError):
            confirmar_venta(venta.id)

        venta.refresh_from_db()

        self.assertEqual(venta.estado, "BORRADOR")

        self.assertFalse(
            MovimientoInventario.objects.filter(referencia=f"VENTA-{venta.id}").exists()
        )

    # PRUEBA 5: Una venta no se confirma dos veces
    def test_venta_no_se_confirma_dos_veces(self):
        compra = self.crear_compra()
        confirmar_compra(compra.id)

        venta = Venta.objects.create(usuario=self.usuario)

        DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=3,
            precio_unitario=Decimal("20.00"),
        )

        confirmar_venta(venta.id)

        with self.assertRaises(ValueError):
            confirmar_venta(venta.id)

        existencia = Existencia.objects.get(producto=self.producto)

        self.assertEqual(existencia.cantidad, 7)

        self.assertEqual(
            MovimientoInventario.objects.filter(
                referencia=f"VENTA-{venta.id}", tipo="SALIDA"
            ).count(),
            1,
        )

    def test_no_modificar_compra_confirmada(self):
        compra = self.crear_compra()
        confirmar_compra(compra.id)

        detalle = compra.detalles.first()
        detalle.cantidad = 50

        with self.assertRaises(ValidationError):
            detalle.save()

    def test_no_modificar_venta_confirmada(self):
        compra = self.crear_compra()
        confirmar_compra(compra.id)

        venta = Venta.objects.create(usuario=self.usuario)

        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=2,
            precio_unitario=Decimal("20.00"),
        )

        confirmar_venta(venta.id)

        detalle.cantidad = 100

        with self.assertRaises(ValidationError):
            detalle.save()
