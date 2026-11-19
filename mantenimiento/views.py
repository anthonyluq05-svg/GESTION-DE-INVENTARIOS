"""Reseteo comercial excepcional. Nunca borra auth ni migraciones."""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.db import connection, transaction
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from compras.models import Compra, DetalleCompra, Proveedor
from inventario.models import Existencia, MovimientoInventario
from productos.models import Categoria, Producto, SecuenciaProducto
from ventas.models import Cliente, Venta, DetalleVenta

# El orden evita relaciones protegidas y conserva los IDs históricos de usuarios.
BORRADO = (
    DetalleVenta, DetalleCompra, MovimientoInventario, Existencia,
    Venta, Compra, Producto, Categoria, Cliente, Proveedor,
)


def _cuenta_tecnica(user):
    return (
        user.is_authenticated and user.is_active and user.is_superuser
        and bool(os.getenv('SGI_MAINTENANCE_USER'))
        and user.username == os.getenv('SGI_MAINTENANCE_USER')
    )


def _ruta_segura():
    # Prohibido almacenar respaldos dentro de static/staticfiles/media o repositorio.
    valor = os.getenv('SGI_PRIVATE_BACKUP_DIR', '').strip()
    if not valor:
        raise ValueError('Configura SGI_PRIVATE_BACKUP_DIR fuera de la carpeta del proyecto.')
    ruta = Path(valor).expanduser().resolve()
    base = Path(settings.BASE_DIR).resolve()
    if ruta == base or base in ruta.parents:
        raise ValueError('El directorio de respaldo debe estar FUERA del proyecto.')
    ruta.mkdir(parents=True, exist_ok=True, mode=0o700)
    return ruta


def _respaldo(ruta):
    db = settings.DATABASES['default']
    if db.get('ENGINE') != 'django.db.backends.postgresql':
        raise ValueError('El restablecimiento requiere PostgreSQL.')
    name = str(db.get('NAME') or '')
    if not name:
        raise ValueError('No se encontró el nombre de la base PostgreSQL.')
    ejecutable = os.getenv('SGI_PG_DUMP', 'pg_dump')
    etiqueta = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archivo = ruta / f'sgi_comercial_antes_de_borrar_{etiqueta}_{os.getpid()}.dump'
    cmd = [ejecutable, '--format=custom', '--no-password', '--file', str(archivo)]
    if db.get('HOST'):
        cmd += ['--host', str(db['HOST'])]
    if db.get('PORT'):
        cmd += ['--port', str(db['PORT'])]
    if db.get('USER'):
        cmd += ['--username', str(db['USER'])]
    cmd += [name]
    env = os.environ.copy()
    env['PGPASSWORD'] = str(db.get('PASSWORD') or '')
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=240, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        archivo.unlink(missing_ok=True)
        raise ValueError(f'No se pudo ejecutar pg_dump: {type(exc).__name__}. Verifica SGI_PG_DUMP.') from exc
    if result.returncode != 0 or not archivo.is_file() or archivo.stat().st_size < 100:
        archivo.unlink(missing_ok=True)
        raise ValueError('Falló el respaldo de PostgreSQL; NO se borró ningún dato. Revisa pg_dump y credenciales.')
    # Comprobar que pg_restore puede leer el índice del archivo antes de continuar.
    restaurador = os.getenv('SGI_PG_RESTORE', '').strip()
    if not restaurador:
        instalacion = Path(ejecutable)
        restaurador = str(instalacion.with_name('pg_restore.exe')) if instalacion.suffix.lower() == '.exe' else 'pg_restore'
    try:
        comprobacion = subprocess.run([restaurador, '--list', str(archivo)],
                                      capture_output=True, text=True, timeout=90, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('El respaldo existe, pero no se pudo verificar con pg_restore. NO se borró ningún dato.') from exc
    if comprobacion.returncode != 0 or not comprobacion.stdout.strip():
        raise ValueError('No se pudo leer el respaldo generado. NO se borró ningún dato.')
    # Ver el índice NO equivale a comprobar una restauración completa.
    return archivo


def _auditar(ruta, evento, usuario, backup=None, cantidades=None):
    registro = {
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'evento': evento,
        'usuario': usuario,
        'backup': str(backup) if backup else None,
        'conteos': cantidades,
    }
    with (ruta / 'auditoria_reseteos.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(registro, ensure_ascii=False) + '\n')


@login_required
@require_http_methods(['GET', 'POST'])
def restablecer_comercio(request):
    if not _cuenta_tecnica(request.user):
        return HttpResponseForbidden('Esta función solo está disponible para la cuenta técnica autorizada.')
    habilitado = os.getenv('SGI_ENABLE_COMMERCIAL_RESET', 'False').lower() == 'true'
    if request.method == 'GET':
        return render(request, 'mantenimiento/restablecer.html', {'habilitado': habilitado})
    if not habilitado:
        return HttpResponseForbidden('El mantenimiento comercial está deshabilitado.')
    clave_hash = os.getenv('SGI_RESET_PASSWORD_HASH', '').strip()
    if not clave_hash or not check_password(request.POST.get('clave', ''), clave_hash):
        messages.error(request, 'No se pudo autorizar el procedimiento.')
        return redirect('productos:restablecer_comercio')
    if request.POST.get('confirmacion', '').strip() != 'BORRAR DATOS COMERCIALES':
        messages.error(request, 'Escribe exactamente BORRAR DATOS COMERCIALES para continuar.')
        return redirect('productos:restablecer_comercio')
    try:
        ruta = _ruta_segura()
        respaldo = _respaldo(ruta)
        _auditar(ruta, 'RESPALDO_CREADO', request.user.username, backup=respaldo)
        cantidades = {}
        with transaction.atomic():
            # Bloqueo exclusivo de todas las tablas comerciales: evita altas concurrentes durante el reseteo.
            if connection.vendor != 'postgresql':
                raise ValueError('El reinicio seguro solo está configurado para PostgreSQL.')
            tablas = ', '.join(connection.ops.quote_name(model._meta.db_table) for model in BORRADO + (SecuenciaProducto,))
            with connection.cursor() as cursor:
                cursor.execute(f'LOCK TABLE {tablas} IN ACCESS EXCLUSIVE MODE')
            for modelo in BORRADO:
                cantidades[modelo.__name__] = modelo.objects.count()
                modelo.objects.all().delete()
            # Reinicia la secuencia de códigos desde 00001 para el nuevo catálogo.
            SecuenciaProducto.objects.all().delete()
            # No se borra auth_user, grupos, permisos ni django_migrations.
        try:
            _auditar(ruta, 'BORRADO_COMPLETADO', request.user.username, backup=respaldo, cantidades=cantidades)
        except OSError:
            # La operación YA se confirmó: no afirmar que se puede deshacer.
            messages.warning(request, 'Datos limpiados, pero falló el registro final de auditoría. Revisa el servidor.')
        else:
            messages.success(request, 'Datos comerciales eliminados. Respaldo conservado fuera del proyecto.')
        return redirect('inicio:dashboard')
    except (ValueError, OSError) as exc:
        messages.error(request, str(exc))
        return redirect('productos:restablecer_comercio')
