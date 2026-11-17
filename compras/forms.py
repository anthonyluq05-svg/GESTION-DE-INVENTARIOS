from django import forms
from django.forms import inlineformset_factory
from .models import Compra, DetalleCompra


class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ["proveedor"]

        widgets = {
            "proveedor": forms.Select(attrs={"class": "form-select"}),
        }


class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ["producto", "cantidad", "costo_unitario"]

        widgets = {
            "producto": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "costo_unitario": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "step": "0.01"}
            ),
        }


DetalleCompraFormSet = inlineformset_factory(
    Compra,
    DetalleCompra,
    form=DetalleCompraForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
