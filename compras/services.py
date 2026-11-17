from django.db import transaction
from .models import Compra
from inventario.services import registrar_entrada


@transaction.atomic
def confirmar_compra(compra_id):

    compra = Compra.objects.select_for_update().get(pk=compra_id)

    if compra.estado != "BORRADOR":
        raise ValueError("La compra ya fue procesada.")

    detalles = list(compra.detalles.select_related("producto"))

    if not detalles:
        raise ValueError("La compra no tiene productos.")

    for detalle in detalles:
        if detalle.cantidad <= 0:
            raise ValueError("Cantidad de compra inválida.")

        if detalle.costo_unitario < 0:
            raise ValueError("Costo unitario inválido.")

    for detalle in detalles:
        registrar_entrada(
            producto=detalle.producto,
            cantidad=detalle.cantidad,
            usuario=compra.usuario,
            referencia=f"COMPRA-{compra.pk}",
        )

    compra.estado = "CONFIRMADA"
    compra.save(update_fields=["estado"])

    return compra
