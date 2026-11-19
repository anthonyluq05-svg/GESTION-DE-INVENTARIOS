from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import redirect, render
from .forms import NuevoUsuarioForm


def exigir_administrador(request):
    if not (request.user.is_superuser or request.user.groups.filter(name='Administrador').exists()):
        raise PermissionDenied('Solo administradores pueden gestionar usuarios.')


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
            user = get_user_model().objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                is_staff=False,
                is_superuser=False,
            )
            rol, _ = Group.objects.get_or_create(name=form.cleaned_data['rol'])
            user.groups.add(rol)
        messages.success(request, f"Usuario {user.username} creado con rol {rol.name}.")
        return redirect('productos:usuarios_lista')
    return render(request, 'usuarios/formulario.html', {'form': form})
