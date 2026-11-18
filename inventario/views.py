from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.db.models import F

from .models import Existencia, MovimientoInventario


@login_required
@permission_required("inventario.view_existencia", raise_exception=True)
def lista_inventario(request):

    existencias = Existencia.objects.select_related(
        "producto", "producto__categoria"
    ).order_by("producto__nombre")

    productos_bajos = existencias.filter(
        cantidad__lte=F("producto__stock_minimo")
    ).count()

    return render(
        request,
        "inventario/lista.html",
        {
            "existencias": existencias,
            "productos_bajos": productos_bajos,
        },
    )


@login_required
@permission_required("inventario.view_movimientoinventario", raise_exception=True)
def lista_movimientos(request):

    movimientos = MovimientoInventario.objects.select_related(
        "producto", "usuario"
    ).order_by("-fecha")

    return render(
        request,
        "inventario/movimientos.html",
        {
            "movimientos": movimientos,
        },
    )
