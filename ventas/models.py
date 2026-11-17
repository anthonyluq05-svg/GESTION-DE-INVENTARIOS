from django.db import models
from django.conf import settings
from productos.models import Producto


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    documento = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    ESTADOS = [
        ("BORRADOR", "Borrador"),
        ("CONFIRMADA", "Confirmada"),
        ("ANULADA", "Anulada"),
    ]

    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, null=True, blank=True
    )

    fecha = models.DateTimeField(auto_now_add=True)

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    estado = models.CharField(max_length=10, choices=ESTADOS, default="BORRADOR")

    def __str__(self):
        return f"Venta #{self.pk}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)

    cantidad = models.PositiveIntegerField()

    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto} - {self.cantidad}"
