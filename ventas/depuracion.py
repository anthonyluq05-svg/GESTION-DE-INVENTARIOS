"""Eliminación mensual segura: solo BORRADORES que no modificaron existencias."""
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from usuarios.views import exigir_administrador
from .models import Venta


@login_required
@require_POST
def eliminar_borradores_mes(request):
    exigir_administrador(request)
    try:
        mes = date.fromisoformat(request.POST['mes'] + '-01')
    except (KeyError, ValueError):
        messages.error(request, 'Selecciona un mes válido (AAAA-MM).')
        return redirect('ventas:lista')
    if request.POST.get('confirmar') != 'ELIMINAR':
        messages.error(request, 'Escribe ELIMINAR para confirmar la operación.')
        return redirect('ventas:lista')
    with transaction.atomic():
        borradores = Venta.objects.select_for_update().filter(
            estado='BORRADOR', fecha__year=mes.year, fecha__month=mes.month
        )
        cantidad = borradores.count()
        borradores.delete()
    messages.success(request, f'Se eliminaron {cantidad} borradores de ventas de {mes:%m/%Y}. Las confirmadas permanecen intactas.')
    return redirect('ventas:lista')

@login_required
@require_POST
def eliminar_borrador(request, pk):
    exigir_administrador(request)
    with transaction.atomic():
        venta = Venta.objects.select_for_update().filter(pk=pk, estado='BORRADOR').first()
        if venta is None:
            messages.error(request, 'Solo se pueden eliminar ventas que estén en borrador.')
        else:
            venta.delete()
            messages.success(request, 'Borrador de venta eliminado.')
    return redirect('ventas:lista')
