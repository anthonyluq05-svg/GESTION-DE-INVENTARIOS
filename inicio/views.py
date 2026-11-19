import calendar
import os
from datetime import date, timedelta
from decimal import Decimal

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
    # Cuatro intervalos sin solapamiento: 1–7, 8–14, 15–21 y 22–fin.
    # La fecha seleccionada se valida y los importes proceden de precios históricos.
    mes_param = request.GET.get('mes', hoy.strftime('%Y-%m'))
    try:
        anio, numero_mes = [int(pieza) for pieza in mes_param.split('-')]
        mes_inicio = date(anio, numero_mes, 1)
        if not 2020 <= anio <= hoy.year + 1:
            raise ValueError('Año no permitido')
    except (ValueError, TypeError):
        mes_inicio = hoy.replace(day=1)
    ultimo_dia = calendar.monthrange(mes_inicio.year, mes_inicio.month)[1]
    mes_fin = mes_inicio.replace(day=ultimo_dia)
    def series(modelo, campo_fecha, importe):
        montos = []
        for comienzo, cierre in [(1, 7), (8, 14), (15, 21), (22, ultimo_dia)]:
            filtros = {
                ('venta__estado' if modelo is DetalleVenta else 'compra__estado'): 'CONFIRMADA',
                f'{campo_fecha}__date__gte': mes_inicio.replace(day=comienzo),
                f'{campo_fecha}__date__lte': mes_inicio.replace(day=cierre),
            }
            montos.append(modelo.objects.filter(**filtros).aggregate(
                total=Sum(importe)
            )['total'] or Decimal('0'))
        techo = max(max(montos), Decimal('1'))
        return [
            {'etiqueta': f'Semana {i + 1}', 'dias': f'{inicio_dia}–{min(fin_dia, ultimo_dia)}',
             'monto': valor, 'altura': max(3, round(float(valor / techo) * 100)) if valor else 2}
            for i, ((inicio_dia, fin_dia), valor) in enumerate(zip(
                [(1, 7), (8, 14), (15, 21), (22, ultimo_dia)], montos
            ))
        ]
    barras_ventas = series(DetalleVenta, 'venta__fecha', subtotal_venta)
    barras_compras = series(DetalleCompra, 'compra__fecha', subtotal_compra)
    # Filtrar solo operaciones confirmadas (también para las gráficas).
    opciones_meses = []
    cursor_mes = hoy.replace(day=1)
    for _ in range(24):
        opciones_meses.append({'valor': cursor_mes.strftime('%Y-%m'),
            'texto': cursor_mes.strftime('%m/%Y')})
        cursor_mes = (cursor_mes - timedelta(days=1)).replace(day=1)
    return render(request, 'inicio/dashboard.html', {
        'barras_ventas': barras_ventas,
        'barras_compras': barras_compras,
        'mes_elegido': mes_inicio.strftime('%Y-%m'),
        'opciones_meses': opciones_meses,
        'puede_restablecer': request.user.is_superuser and request.user.username == os.getenv('SGI_MAINTENANCE_USER', ''),
        'total_productos': total_productos,
        'total_unidades': total_unidades,
        'stock_bajo': stock_bajo,
        'ventas_hoy': ventas_hoy,
        'compras_hoy': compras_hoy,
        'ultimas_ventas': ultimas_ventas,
    })
