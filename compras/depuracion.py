"""Eliminación mensual segura: solo BORRADORES que no modificaron existencias."""
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from usuarios.views import exigir_administrador
from .models import Compra


@login_required
@require_POST
def eliminar_borradores_mes(request):
    exigir_administrador(request)
    try:
        mes = date.fromisoformat(request.POST['mes'] + '-01')
    except (KeyError, ValueError):
        messages.error(request, 'Selecciona un mes válido (AAAA-MM).')
        return redirect('compras:lista')
    if request.POST.get('confirmar') != 'ELIMINAR':
        messages.error(request, 'Escribe ELIMINAR para confirmar la operación.')
        return redirect('compras:lista')
    with transaction.atomic():
        borradores = Compra.objects.select_for_update().filter(
            estado='BORRADOR', fecha__year=mes.year, fecha__month=mes.month
        )
        cantidad = borradores.count()
        borradores.delete()
    messages.success(request, f'Se eliminaron {cantidad} borradores de compras de {mes:%m/%Y}. Las confirmadas permanecen intactas.')
    return redirect('compras:lista')

@login_required
@require_POST
def eliminar_borrador(request, pk):
    exigir_administrador(request)
    with transaction.atomic():
        compra = Compra.objects.select_for_update().filter(pk=pk, estado='BORRADOR').first()
        if compra is None:
            messages.error(request, 'Solo se pueden eliminar compras que estén en borrador.')
        else:
            compra.delete()
            messages.success(request, 'Borrador de compra eliminado.')
    return redirect('compras:lista')
