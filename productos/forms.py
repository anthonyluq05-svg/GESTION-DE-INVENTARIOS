from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "categoria",
            "precio_compra",
            "precio_venta",
            "stock_minimo",
            "activo",
        ]

        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "precio_compra": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "precio_venta": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "stock_minimo": forms.NumberInput(
                attrs={"class": "form-control", "min": "0"}
            ),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
