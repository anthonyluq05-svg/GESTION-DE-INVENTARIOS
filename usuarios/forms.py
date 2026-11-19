from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import Group


class NuevoUsuarioForm(forms.Form):
    username = forms.CharField(max_length=150, label='Nombre de usuario', widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    first_name = forms.CharField(max_length=150, required=False, label='Nombres', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, label='Apellidos', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, label='Correo', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    rol = forms.ChoiceField(choices=[('Vendedor', 'Vendedor'), ('Administrador', 'Administrador')], widget=forms.Select(attrs={'class': 'form-select'}))
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Repetir contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}))

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if get_user_model().objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Ese nombre de usuario ya existe.')
        return username

    def clean(self):
        data = super().clean()
        if data.get('password1') and data.get('password2') and data['password1'] != data['password2']:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        if data.get('password1'):
            try:
                password_validation.validate_password(data['password1'])
            except forms.ValidationError as e:
                self.add_error('password1', e)
        return data
