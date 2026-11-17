from django.db import transaction
from django.db.models import Sum

from .models import Venta
from inventario.models import Existencia
from inventario.services import registrar_salida


@transaction.atomic
def confirmar_venta(venta_id):

    venta = Venta.objects.select_for_update().get(pk=venta_id)

    if venta.estado != "BORRADOR":
        raise ValueError("La venta ya fue procesada.")

    detalles = list(venta.detalles.select_related("producto"))

    if not detalles:
        raise ValueError("La venta no tiene productos.")

    for detalle in detalles:
        if detalle.cantidad <= 0:
            raise ValueError("Cantidad inválida.")

        if detalle.precio_unitario < 0:
            raise ValueError("Precio inválido.")

    cantidades = venta.detalles.values("producto_id").annotate(total=Sum("cantidad"))

    for item in cantidades:
        existencia = Existencia.objects.filter(producto_id=item["producto_id"]).first()

        if existencia is None or existencia.cantidad < item["total"]:
            raise ValueError("Stock insuficiente para confirmar la venta.")

    for detalle in detalles:
        registrar_salida(
            producto=detalle.producto,
            cantidad=detalle.cantidad,
            usuario=venta.usuario,
            referencia=f"VENTA-{venta.pk}",
        )

    venta.estado = "CONFIRMADA"
    venta.save(update_fields=["estado"])

    return venta
