from django.core.exceptions import ValidationError
from django.db import models, transaction


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']


class SecuenciaProducto(models.Model):
    """Contador único, independiente de los IDs y sin reutilizar números."""
    nombre = models.CharField(max_length=20, primary_key=True, default='producto')
    siguiente = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.nombre}: {self.siguiente}'


class Producto(models.Model):
    codigo = models.CharField(max_length=30, unique=True, editable=False, blank=True)
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name='productos'
    )
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.PositiveIntegerField(default=5)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # El código nunca es editable, ni desde un formulario manipulado.
            self.codigo = type(self).objects.values_list(
                'codigo', flat=True
            ).get(pk=self.pk)
            return super().save(*args, **kwargs)

        with transaction.atomic():
            secuencia, _ = SecuenciaProducto.objects.get_or_create(
                nombre='producto', defaults={'siguiente': 1}
            )
            secuencia = SecuenciaProducto.objects.select_for_update().get(
                pk=secuencia.pk
            )
            numero = secuencia.siguiente
            # Respeta productos históricos con códigos 00001...10000.
            while numero <= 10000 and type(self).objects.filter(
                codigo=f'{numero:05d}'
            ).exists():
                numero += 1
            if numero > 10000:
                raise ValidationError('Se alcanzó el límite de 10 000 códigos.')

            self.codigo = f'{numero:05d}'
            super().save(*args, **kwargs)
            secuencia.siguiente = numero + 1
            secuencia.save(update_fields=['siguiente'])

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
