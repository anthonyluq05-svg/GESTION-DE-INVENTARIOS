from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper

from openpyxl import Workbook
from openpyxl.styles import Font

from ventas.models import DetalleVenta


def es_administrador(user):
    return user.is_active and (
        user.is_superuser or user.groups.filter(name="Administrador").exists()
    )


def obtener_ventas(request):
    detalles = (
        DetalleVenta.objects.filter(venta__estado="CONFIRMADA")
        .select_related("venta", "venta__cliente", "producto")
        .order_by("-venta__fecha")
    )

    inicio = request.GET.get("inicio", "")
    fin = request.GET.get("fin", "")

    try:
        if inicio:
            date.fromisoformat(inicio)
            detalles = detalles.filter(venta__fecha__date__gte=inicio)

        if fin:
            date.fromisoformat(fin)
            detalles = detalles.filter(venta__fecha__date__lte=fin)
    except ValueError:
        raise ValueError("Las fechas ingresadas no son válidas.")

    return detalles


@login_required
@user_passes_test(es_administrador)
def reporte_ventas(request):
    try:
        detalles = obtener_ventas(request)
    except ValueError as error:
        return render(
            request,
            "reportes/ventas.html",
            {
                "error": str(error),
                "detalles": [],
                "total": 0,
            },
        )

    subtotal = ExpressionWrapper(
        F("cantidad") * F("precio_unitario"),
        output_field=DecimalField(max_digits=18, decimal_places=2),
    )

    total = detalles.aggregate(total=Sum(subtotal))["total"] or Decimal("0.00")

    return render(
        request,
        "reportes/ventas.html",
        {
            "detalles": detalles,
            "total": total,
        },
    )


@login_required
@user_passes_test(es_administrador)
def exportar_ventas(request):
    try:
        detalles = obtener_ventas(request)
    except ValueError as error:
        return HttpResponse(str(error), status=400)

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Ventas"

    hoja.append(
        [
            "Venta",
            "Fecha",
            "Cliente",
            "Producto",
            "Cantidad",
            "Precio unitario",
            "Subtotal",
        ]
    )

    for celda in hoja[1]:
        celda.font = Font(bold=True)

    for detalle in detalles:
        hoja.append(
            [
                detalle.venta_id,
                detalle.venta.fecha.strftime("%d/%m/%Y"),
                detalle.venta.cliente.nombre
                if detalle.venta.cliente
                else "Público general",
                detalle.producto.nombre,
                detalle.cantidad,
                float(detalle.precio_unitario),
                float(detalle.subtotal),
            ]
        )

    for columna, ancho in {
        "A": 12,
        "B": 16,
        "C": 25,
        "D": 30,
        "E": 12,
        "F": 18,
        "G": 18,
    }.items():
        hoja.column_dimensions[columna].width = ancho

    for fila in hoja.iter_rows(min_row=2):
        fila[5].number_format = "#,##0.00"
        fila[6].number_format = "#,##0.00"

    respuesta = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    )

    respuesta["Content-Disposition"] = 'attachment; filename="reporte_ventas.xlsx"'

    libro.save(respuesta)

    return respuesta
