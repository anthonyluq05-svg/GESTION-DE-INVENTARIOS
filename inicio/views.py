from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import render
from django.utils import timezone

from compras.models import DetalleCompra
from inventario.models import Existencia
from productos.models import Producto
from ventas.models import DetalleVenta, Venta


def rol_autorizado(user):
    return user.is_active and (
        user.is_superuser or
        user.groups.filter(name__in=['Administrador', 'Vendedor']).exists()
    )


@login_required
@user_passes_test(rol_autorizado)
def dashboard(request):
    hoy = timezone.localdate()
    total_productos = Producto.objects.filter(activo=True).count()
    total_unidades = Existencia.objects.aggregate(total=Sum('cantidad'))['total'] or 0
    stock_bajo = Existencia.objects.filter(
        producto__activo=True,
        cantidad__lte=F('producto__stock_minimo')
    ).count()
    subtotal_venta = ExpressionWrapper(
        F('cantidad') * F('precio_unitario'),
        output_field=DecimalField(max_digits=18, decimal_places=2)
    )
    ventas_hoy = DetalleVenta.objects.filter(
        venta__estado='CONFIRMADA', venta__fecha__date=hoy
    ).aggregate(total=Sum(subtotal_venta))['total'] or 0
    subtotal_compra = ExpressionWrapper(
        F('cantidad') * F('costo_unitario'),
        output_field=DecimalField(max_digits=18, decimal_places=2)
    )
    compras_hoy = DetalleCompra.objects.filter(
        compra__estado='CONFIRMADA', compra__fecha__date=hoy
    ).aggregate(total=Sum(subtotal_compra))['total'] or 0
    ultimas_ventas = Venta.objects.filter(
        estado='CONFIRMADA'
    ).select_related('cliente', 'usuario').order_by('-fecha')[:5]
    return render(request, 'inicio/dashboard.html', {
        'total_productos': total_productos,
        'total_unidades': total_unidades,
        'stock_bajo': stock_bajo,
        'ventas_hoy': ventas_hoy,
        'compras_hoy': compras_hoy,
        'ultimas_ventas': ultimas_ventas,
    })
