from django import forms
from django.forms import inlineformset_factory
from .models import Venta, DetalleVenta


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente"]

        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ["producto", "cantidad", "precio_unitario"]

        widgets = {
            "producto": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "precio_unitario": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.01"}
            ),
        }


DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
