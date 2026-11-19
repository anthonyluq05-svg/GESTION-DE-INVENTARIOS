from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import EditarUsuarioForm, NuevoUsuarioForm


def exigir_administrador(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()):
        raise PermissionDenied('Solo administradores pueden gestionar usuarios.')


def es_admin(cuenta):
    return cuenta.is_superuser or cuenta.groups.filter(name='Administrador').exists()


def ultimo_admin(cuenta):
    if not es_admin(cuenta) or not cuenta.is_active:
        return False
    User = get_user_model()
    return not User.objects.filter(is_active=True).exclude(pk=cuenta.pk).filter(
        Q(is_superuser=True) |
        Q(groups__name='Administrador')
    ).distinct().exists()


@login_required
def lista_usuarios(request):
    exigir_administrador(request)
    usuarios = get_user_model().objects.prefetch_related('groups').order_by('username')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
def crear_usuario(request):
    exigir_administrador(request)
    form = NuevoUsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            cuenta = get_user_model().objects.create_user(
                username=form.cleaned_data['username'], password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'], is_staff=False, is_superuser=False,
            )
            grupo, _ = Group.objects.get_or_create(name=form.cleaned_data['rol'])
            cuenta.groups.add(grupo)
        messages.success(request, 'Usuario creado correctamente.')
        return redirect('productos:usuarios_lista')
    return render(request, 'usuarios/formulario.html', {'form': form, 'modo': 'crear'})


@login_required
def editar_usuario(request, pk):
    exigir_administrador(request)
    cuenta = get_object_or_404(get_user_model(), pk=pk)
    if cuenta.is_superuser:
        messages.error(request, 'Los superusuarios se gestionan desde Django Admin.')
        return redirect('productos:usuarios_lista')
    grupo = cuenta.groups.filter(name__in=['Administrador','Vendedor']).first()
    initial = dict(first_name=cuenta.first_name, last_name=cuenta.last_name,
                   email=cuenta.email, is_active=cuenta.is_active,
                   rol=grupo.name if grupo else 'Vendedor')
    form = EditarUsuarioForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        if cuenta.pk == request.user.pk and not form.cleaned_data['is_active']:
            form.add_error('is_active', 'No puedes desactivar tu propia sesión.')
        elif ultimo_admin(cuenta) and (form.cleaned_data['rol'] != 'Administrador' or not form.cleaned_data['is_active']):
            form.add_error('rol', 'Debe permanecer al menos un administrador activo.')
        else:
            with transaction.atomic():
                cuenta.first_name = form.cleaned_data['first_name']
                cuenta.last_name = form.cleaned_data['last_name']
                cuenta.email = form.cleaned_data['email']
                cuenta.is_active = form.cleaned_data['is_active']
                if form.cleaned_data['password1']:
                    cuenta.set_password(form.cleaned_data['password1'])
                cuenta.save()
                grupo, _ = Group.objects.get_or_create(name=form.cleaned_data['rol'])
                cuenta.groups.set([grupo])
            messages.success(request, 'Usuario actualizado.')
            return redirect('productos:usuarios_lista')
    return render(request, 'usuarios/formulario.html', {'form': form, 'modo': 'editar', 'cuenta': cuenta})


@login_required
@require_POST
def eliminar_usuario(request, pk):
    exigir_administrador(request)
    cuenta = get_object_or_404(get_user_model(), pk=pk)
    if cuenta.pk == request.user.pk or cuenta.is_superuser or ultimo_admin(cuenta):
        messages.error(request, 'No se puede desactivar esta cuenta de administrador.')
    else:
        cuenta.is_active = False
        cuenta.save(update_fields=['is_active'])
        messages.success(request, f'Usuario {cuenta.username} desactivado. Su historial se conserva.')
    return redirect('productos:usuarios_lista')
