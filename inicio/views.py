from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.shortcuts import render
from django.utils import timezone

from productos.models import Producto
from compras.models import Compra, DetalleCompra
from ventas.models import Venta, DetalleVenta
from inventario.models import Existencia


@login_required
def dashboard(request):
    hoy = timezone.localdate()

    # Productos
    total_productos = Producto.objects.filter(activo=True).count()

    # Existencias
    total_unidades = Existencia.objects.aggregate(total=Sum("cantidad"))["total"] or 0

    stock_bajo = Existencia.objects.filter(
        cantidad__lte=F("producto__stock_minimo"), producto__activo=True
    ).count()

    # Valor de cada línea de venta
    subtotal_venta = ExpressionWrapper(
        F("cantidad") * F("precio_unitario"),
        output_field=DecimalField(max_digits=18, decimal_places=2),
    )

    # Ventas confirmadas de hoy
    ventas_hoy = (
        DetalleVenta.objects.filter(
            venta__estado="CONFIRMADA", venta__fecha__date=hoy
        ).aggregate(total=Sum(subtotal_venta))["total"]
        or 0
    )

    # Compras confirmadas de hoy
    subtotal_compra = ExpressionWrapper(
        F("cantidad") * F("costo_unitario"),
        output_field=DecimalField(max_digits=18, decimal_places=2),
    )

    compras_hoy = (
        DetalleCompra.objects.filter(
            compra__estado="CONFIRMADA", compra__fecha__date=hoy
        ).aggregate(total=Sum(subtotal_compra))["total"]
        or 0
    )

    ultimas_ventas = (
        Venta.objects.filter(estado="CONFIRMADA")
        .select_related("cliente", "usuario")
        .order_by("-fecha")[:5]
    )

    context = {
        "total_productos": total_productos,
        "total_unidades": total_unidades,
        "stock_bajo": stock_bajo,
        "ventas_hoy": ventas_hoy,
        "compras_hoy": compras_hoy,
        "ultimas_ventas": ultimas_ventas,
    }

    return render(request, "inicio/dashboard.html", context)
