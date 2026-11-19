from django import forms
from django.forms import inlineformset_factory
from .models import Compra, DetalleCompra, Proveedor


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'telefono', 'correo', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ruc': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor']
        widgets = {'proveedor': forms.Select(attrs={'class': 'form-select'})}


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor que cero.')
        return cantidad


DetalleCompraFormSet = inlineformset_factory(
    Compra, DetalleCompra, form=DetalleCompraForm,
    extra=1, min_num=1, validate_min=True,
    max_num=50, validate_max=True, can_delete=True,
)
