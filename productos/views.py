from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto


class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'productos.view_producto'
    model = Producto
    template_name = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        return Producto.objects.select_related('categoria').order_by('nombre')


class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'productos.add_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/formulario.html'
    success_url = reverse_lazy('productos:lista')


class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'productos.change_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/formulario.html'
    success_url = reverse_lazy('productos:lista')


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'productos.delete_producto'
    model = Producto
    template_name = 'productos/confirmar_eliminar.html'
    success_url = reverse_lazy('productos:lista')

    def form_valid(self, form):
        producto = self.get_object()
        try:
            producto.delete()
        except ProtectedError:
            messages.error(
                self.request,
                'No se puede eliminar: el producto tiene inventario u operaciones '
                'relacionadas. Edítalo y desactívalo en su lugar.'
            )
            return redirect(self.success_url)
        messages.success(self.request, 'Producto eliminado correctamente.')
        return redirect(self.success_url)


class CategoriaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'productos.view_categoria'
    model = Categoria
    template_name = 'categorias/lista.html'
    context_object_name = 'categorias'


class CategoriaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'productos.add_categoria'
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categorias/formulario.html'
    success_url = reverse_lazy('productos:categorias')
