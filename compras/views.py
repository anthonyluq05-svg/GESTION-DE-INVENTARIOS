from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Compra
from .forms import CompraForm, DetalleCompraFormSet
from .services import confirmar_compra


@login_required
@permission_required("compras.view_compra", raise_exception=True)
def lista_compras(request):
    compras = Compra.objects.select_related("proveedor", "usuario").order_by("-fecha")

    return render(request, "compras/lista.html", {"compras": compras})


@login_required
@permission_required("compras.add_compra", raise_exception=True)
def crear_compra(request):
    compra = Compra(usuario=request.user)

    if request.method == "POST":
        form = CompraForm(request.POST, instance=compra)
        formset = DetalleCompraFormSet(request.POST, instance=compra)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                compra = form.save(commit=False)
                compra.usuario = request.user
                compra.estado = "BORRADOR"
                compra.save()

                formset.instance = compra
                formset.save()

            messages.success(request, "Compra registrada correctamente.")
            return redirect("compras:lista")

    else:
        form = CompraForm(instance=compra)
        formset = DetalleCompraFormSet(instance=compra)

    return render(
        request, "compras/formulario.html", {"form": form, "formset": formset}
    )


@login_required
@permission_required("compras.change_compra", raise_exception=True)
def confirmar_compra_view(request, pk):
    if request.method != "POST":
        return redirect("compras:lista")

    compra = get_object_or_404(Compra, pk=pk)

    try:
        confirmar_compra(compra.pk)
        messages.success(request, "Compra confirmada. Stock actualizado.")
    except ValueError as error:
        messages.error(request, str(error))

    return redirect("compras:lista")
