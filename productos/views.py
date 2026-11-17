from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .models import Producto
from .forms import ProductoForm


class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = "productos/lista.html"
    context_object_name = "productos"
    paginate_by = 10

    def get_queryset(self):
        return Producto.objects.select_related("categoria").order_by("nombre")


class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/formulario.html"
    success_url = reverse_lazy("productos:lista")


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/formulario.html"
    success_url = reverse_lazy("productos:lista")


# Create your views here.
