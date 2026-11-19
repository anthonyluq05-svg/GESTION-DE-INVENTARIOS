"""CRUD de clientes; no altera ventas antiguas ni permite borrado si hay historial."""
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError, RestrictedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from usuarios.views import exigir_administrador
from .models import Cliente, Venta


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-check-input' if isinstance(field.widget, forms.CheckboxInput) else 'form-control'


@login_required
def lista_clientes(request):
    exigir_administrador(request)
    return render(request, 'clientes/lista.html', {'clientes': Cliente.objects.all().order_by('pk')})


@login_required
def crear_cliente(request):
    exigir_administrador(request)
    form = ClienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cliente registrado.')
        return redirect('productos:clientes_lista')
    return render(request, 'clientes/formulario.html', {'form': form})


@login_required
def editar_cliente(request, pk):
    exigir_administrador(request)
    cliente = get_object_or_404(Cliente, pk=pk)
    form = ClienteForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cliente actualizado.')
        return redirect('productos:clientes_lista')
    return render(request, 'clientes/formulario.html', {'form': form, 'cliente': cliente})


@login_required
@require_POST
def eliminar_cliente(request, pk):
    exigir_administrador(request)
    cliente = get_object_or_404(Cliente, pk=pk)
    if Venta.objects.filter(cliente=cliente).exists():
        messages.error(request, 'Este cliente tiene ventas asociadas; no se puede eliminar.')
    else:
        try:
            with transaction.atomic():
                cliente.delete()
        except (ProtectedError, RestrictedError, IntegrityError):
            messages.error(request, 'No se puede eliminar el cliente por registros vinculados.')
        else:
            messages.success(request, 'Cliente eliminado.')
    return redirect('productos:clientes_lista')
