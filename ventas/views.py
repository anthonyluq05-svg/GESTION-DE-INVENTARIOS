from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import Venta
from .forms import VentaForm, DetalleVentaFormSet
from .services import confirmar_venta


@login_required
@permission_required("ventas.view_venta", raise_exception=True)
def lista_ventas(request):
    ventas = Venta.objects.select_related("cliente", "usuario").order_by("-fecha")

    return render(request, "ventas/lista.html", {"ventas": ventas})


@login_required
@permission_required("ventas.add_venta", raise_exception=True)
def crear_venta(request):
    venta = Venta(usuario=request.user)

    if request.method == "POST":
        form = VentaForm(request.POST, instance=venta)
        formset = DetalleVentaFormSet(request.POST, instance=venta)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                venta = form.save(commit=False)
                venta.usuario = request.user
                venta.estado = "BORRADOR"
                venta.save()

                formset.instance = venta
                formset.save()

            messages.success(request, "Venta registrada correctamente.")
            return redirect("ventas:lista")
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta)

    return render(request, "ventas/formulario.html", {"form": form, "formset": formset})


@login_required
@permission_required("ventas.change_venta", raise_exception=True)
def confirmar_venta_view(request, pk):
    if request.method != "POST":
        return redirect("ventas:lista")

    venta = get_object_or_404(Venta, pk=pk)

    try:
        confirmar_venta(venta.pk)
        messages.success(request, "Venta confirmada. Stock actualizado.")
    except ValueError as error:
        messages.error(request, str(error))

    return redirect("ventas:lista")
