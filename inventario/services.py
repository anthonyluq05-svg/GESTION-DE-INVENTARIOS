from django.db import transaction
from .models import Existencia, MovimientoInventario


@transaction.atomic
def registrar_entrada(producto, cantidad, usuario, referencia=""):

    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    existencia, creada = Existencia.objects.get_or_create(
        producto=producto, defaults={"cantidad": 0}
    )

    existencia = Existencia.objects.select_for_update().get(pk=existencia.pk)

    existencia.cantidad += cantidad
    existencia.save(update_fields=["cantidad"])

    movimiento = MovimientoInventario.objects.create(
        producto=producto,
        tipo="ENTRADA",
        cantidad=cantidad,
        usuario=usuario,
        referencia=referencia,
    )

    return movimiento
