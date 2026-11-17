from django.db import models
from django.conf import settings
from productos.models import Producto


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=11, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Compra(models.Model):
    ESTADOS = [
        ("BORRADOR", "Borrador"),
        ("CONFIRMADA", "Confirmada"),
        ("ANULADA", "Anulada"),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="BORRADOR")

    def __str__(self):
        return f"Compra #{self.pk}"


class DetalleCompra(models.Model):
    compra = models.ForeignKey(
        Compra, on_delete=models.CASCADE, related_name="detalles"
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.costo_unitario

    def __str__(self):
        return f"{self.producto} - {self.cantidad}"
