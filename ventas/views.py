from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import DetalleVentaFormSet, VentaForm
from .models import Venta
from .services import confirmar_venta


@login_required
@permission_required('ventas.view_venta', raise_exception=True)
def lista_ventas(request):
    ventas = Venta.objects.select_related('cliente', 'usuario').order_by('-fecha')
    return render(request, 'ventas/lista.html', {'ventas': ventas})


@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    venta = Venta(usuario=request.user)
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        formset = DetalleVentaFormSet(request.POST, instance=venta)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta = form.save(commit=False)
                venta.usuario = request.user
                venta.estado = 'BORRADOR'
                venta.save()
                formset.instance = venta
                detalles = formset.save(commit=False)
                for detalle in detalles:
                    detalle.venta = venta
                    detalle.precio_unitario = detalle.producto.precio_venta
                    detalle.costo_unitario = detalle.producto.precio_compra
                    detalle.save()
            messages.success(request, 'Venta registrada en borrador.')
            return redirect('ventas:lista')
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta)
    return render(request, 'ventas/formulario.html', {
        'form': form, 'formset': formset,
    })


@login_required
@permission_required('ventas.change_venta', raise_exception=True)
@require_POST
def confirmar_venta_view(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    try:
        confirmar_venta(venta.pk)
        messages.success(request, 'Venta confirmada: inventario actualizado.')
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect('ventas:lista')
