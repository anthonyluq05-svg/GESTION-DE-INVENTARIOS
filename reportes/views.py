from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper

from openpyxl import Workbook
from openpyxl.styles import Font

from ventas.models import DetalleVenta

from compras.models import DetalleCompra
from inventario.models import Existencia


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


@login_required
@user_passes_test(es_administrador)
def reporte_compras(request):
    detalles = (
        DetalleCompra.objects.filter(compra__estado="CONFIRMADA")
        .select_related("compra", "compra__proveedor", "producto")
        .order_by("-compra__fecha")
    )

    inicio = request.GET.get("inicio")
    fin = request.GET.get("fin")

    try:
        if inicio:
            date.fromisoformat(inicio)
            detalles = detalles.filter(compra__fecha__date__gte=inicio)

        if fin:
            date.fromisoformat(fin)
            detalles = detalles.filter(compra__fecha__date__lte=fin)
    except ValueError:
        return render(
            request,
            "reportes/compras.html",
            {"detalles": [], "total": 0, "error": "Fecha inválida."},
        )

    total = sum((detalle.subtotal for detalle in detalles), Decimal("0.00"))

    return render(
        request,
        "reportes/compras.html",
        {
            "detalles": detalles,
            "total": total,
        },
    )


@login_required
@user_passes_test(es_administrador)
def reporte_inventario(request):
    existencias = Existencia.objects.select_related(
        "producto", "producto__categoria"
    ).order_by("producto__nombre")

    return render(request, "reportes/inventario.html", {"existencias": existencias})


@login_required
@user_passes_test(es_administrador)
def exportar_inventario(request):
    existencias = Existencia.objects.select_related(
        "producto", "producto__categoria"
    ).order_by("producto__nombre")

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Inventario"

    hoja.append(
        ["Código", "Producto", "Categoría", "Cantidad", "Stock mínimo", "Precio venta"]
    )

    for celda in hoja[1]:
        celda.font = Font(bold=True)

    for existencia in existencias:
        producto = existencia.producto

        hoja.append(
            [
                producto.codigo,
                producto.nombre,
                producto.categoria.nombre,
                existencia.cantidad,
                producto.stock_minimo,
                float(producto.precio_venta),
            ]
        )

    for columna, ancho in {
        "A": 18,
        "B": 30,
        "C": 25,
        "D": 15,
        "E": 18,
        "F": 20,
    }.items():
        hoja.column_dimensions[columna].width = ancho

    for fila in hoja.iter_rows(min_row=2):
        fila[5].number_format = "#,##0.00"

    respuesta = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    )

    respuesta["Content-Disposition"] = 'attachment; filename="reporte_inventario.xlsx"'

    libro.save(respuesta)
    return respuesta


@login_required
@user_passes_test(es_administrador)
def exportar_compras(request):
    detalles = (
        DetalleCompra.objects.filter(compra__estado="CONFIRMADA")
        .select_related("compra", "compra__proveedor", "producto")
        .order_by("-compra__fecha")
    )

    inicio = request.GET.get("inicio")
    fin = request.GET.get("fin")

    try:
        if inicio:
            date.fromisoformat(inicio)
            detalles = detalles.filter(compra__fecha__date__gte=inicio)

        if fin:
            date.fromisoformat(fin)
            detalles = detalles.filter(compra__fecha__date__lte=fin)

    except ValueError:
        return HttpResponse("Fecha inválida.", status=400)

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Compras"

    hoja.append(
        [
            "Compra",
            "Fecha",
            "Proveedor",
            "Producto",
            "Cantidad",
            "Costo unitario",
            "Subtotal",
        ]
    )

    for celda in hoja[1]:
        celda.font = Font(bold=True)

    for detalle in detalles:
        hoja.append(
            [
                detalle.compra_id,
                detalle.compra.fecha.strftime("%d/%m/%Y"),
                detalle.compra.proveedor.nombre,
                detalle.producto.nombre,
                detalle.cantidad,
                float(detalle.costo_unitario),
                float(detalle.subtotal),
            ]
        )

    for columna, ancho in {
        "A": 12,
        "B": 16,
        "C": 30,
        "D": 30,
        "E": 14,
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

    respuesta["Content-Disposition"] = 'attachment; filename="reporte_compras.xlsx"'

    libro.save(respuesta)

    return respuesta
