from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction, IntegrityError
from django.db.models.deletion import ProtectedError, RestrictedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CompraForm, DetalleCompraFormSet, ProveedorForm
from .models import Compra, Proveedor, DetalleCompra
from .services import confirmar_compra


@login_required
@permission_required('compras.view_compra', raise_exception=True)
def lista_compras(request):
    compras = list(Compra.objects.select_related('proveedor', 'usuario').order_by('-fecha'))
    detalles = DetalleCompra.objects.filter(compra_id__in=[c.pk for c in compras]).select_related('producto').order_by('pk')
    por_compra = {}
    for item in detalles:
        por_compra.setdefault(item.compra_id, []).append(item)
    for compra in compras:
        compra.detalles_vista = por_compra.get(compra.pk, [])
    return render(request, 'compras/lista.html', {'compras': compras})


@login_required
@permission_required('compras.add_compra', raise_exception=True)
def crear_compra(request):
    compra = Compra(usuario=request.user)
    if request.method == 'POST':
        form = CompraForm(request.POST, instance=compra)
        formset = DetalleCompraFormSet(request.POST, instance=compra)
        if form.is_valid() and formset.is_valid():
            try:
                # Se guarda y confirma como una ÚNICA transacción: si falla stock
                # o algún detalle, no quedan compras parciales ni borradores.
                with transaction.atomic():
                    compra = form.save(commit=False)
                    compra.usuario = request.user
                    compra.estado = 'BORRADOR'
                    compra.save()
                    formset.instance = compra
                    for detalle in formset.save(commit=False):
                        detalle.compra = compra
                        detalle.costo_unitario = detalle.producto.precio_compra
                        detalle.save()
                    confirmar_compra(compra.pk)
            except ValueError as exc:
                form.add_error(None, str(exc))
            else:
                messages.success(request, 'Compra registrada: inventario actualizado.')
                return redirect('compras:lista')
    else:
        form = CompraForm(instance=compra)
        formset = DetalleCompraFormSet(instance=compra)
    return render(request, 'compras/formulario.html', {
        'form': form, 'formset': formset,
    })


@login_required
@permission_required('compras.change_compra', raise_exception=True)
@require_POST
def confirmar_compra_view(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    try:
        confirmar_compra(compra.pk)
        messages.success(request, 'Compra confirmada: inventario actualizado.')
    except ValueError as exc:
        messages.error(request, str(exc))
    return redirect('compras:lista')


@login_required
@permission_required('compras.view_proveedor', raise_exception=True)
def lista_proveedores(request):
    return render(request, 'proveedores/lista.html', {
        'proveedores': Proveedor.objects.order_by('nombre')
    })


@login_required
@permission_required('compras.add_proveedor', raise_exception=True)
def crear_proveedor(request):
    form = ProveedorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Proveedor registrado correctamente.')
        return redirect('compras:proveedores')
    return render(request, 'proveedores/formulario.html', {'form': form})


@login_required
@permission_required('compras.change_proveedor', raise_exception=True)
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(request.POST or None, instance=proveedor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Proveedor actualizado correctamente.')
        return redirect('compras:proveedores')
    return render(request, 'proveedores/formulario.html', {'form': form, 'proveedor': proveedor})


@login_required
@permission_required('compras.delete_proveedor', raise_exception=True)
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        # Protección adicional incluso si la FK Compra.proveedor usa CASCADE.
        if Compra.objects.filter(proveedor=proveedor).exists():
            messages.error(request, 'Este proveedor tiene compras relacionadas. Desactívalo desde Editar en lugar de eliminarlo.')
            return redirect('compras:proveedores')
        try:
            with transaction.atomic():
                proveedor.delete()
        except (ProtectedError, RestrictedError, IntegrityError):
            messages.error(request, 'Este proveedor tiene compras relacionadas. Desactívalo desde Editar en lugar de eliminarlo.')
        else:
            messages.success(request, 'Proveedor eliminado correctamente.')
        return redirect('compras:proveedores')
    return render(request, 'proveedores/confirmar_eliminar.html', {'proveedor': proveedor})
