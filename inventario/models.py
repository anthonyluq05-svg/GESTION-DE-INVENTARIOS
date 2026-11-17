from django.db import models
from django.conf import settings
from productos.models import Producto


class Existencia(models.Model):
    producto = models.OneToOneField(
        Producto, on_delete=models.PROTECT, related_name="existencia"
    )
    cantidad = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.producto.nombre}: {self.cantidad}"


class MovimientoInventario(models.Model):
    TIPOS = [
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
    ]

    producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name="movimientos"
    )

    tipo = models.CharField(max_length=10, choices=TIPOS)

    cantidad = models.PositiveIntegerField()

    fecha = models.DateTimeField(auto_now_add=True)

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    referencia = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.tipo}: {self.producto.nombre} ({self.cantidad})"
