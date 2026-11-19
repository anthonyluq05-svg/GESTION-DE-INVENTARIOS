from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, DetalleVenta, Venta


class VentaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(), required=False,
        empty_label='Público general',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Venta
        fields = ['cliente']


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
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


DetalleVentaFormSet = inlineformset_factory(
    Venta, DetalleVenta, form=DetalleVentaForm,
    extra=1, min_num=1, validate_min=True,
    max_num=50, validate_max=True, can_delete=True,
)
