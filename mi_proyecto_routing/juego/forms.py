"""Validators reutilizables. No se convierten strings ni booleanos a números."""

from django import forms

from .models import Habilidad, Personaje


# Incluye los tipos existentes en el fixture de la actividad 09.
TIPOS_VALIDOS = [(tipo, tipo.capitalize()) for tipo in (
    'guerrero', 'maga', 'elfo', 'asesino', 'enano', 'arquera', 'orco',
)]


class EnteroJSON(forms.IntegerField):
    def to_python(self, value):
        if value is not None and type(value) is not int:
            raise forms.ValidationError('Debe ser un número entero JSON.', code='invalid')
        return super().to_python(value)


class TextoJSON(forms.CharField):
    def to_python(self, value):
        if value is not None and not isinstance(value, str):
            raise forms.ValidationError('Debe ser texto.', code='invalid')
        return super().to_python(value)


class CamposEstrictos:
    def clean(self):
        datos = super().clean()
        for campo in self.fields:
            if campo in self.data and self.data[campo] is None and campo not in self.errors:
                self.add_error(campo, 'No admite null.')
        desconocidos = sorted(set(self.data) - set(self.fields))
        if desconocidos:
            raise forms.ValidationError('Campos desconocidos: ' + ', '.join(desconocidos))
        return datos


class PersonajeForm(CamposEstrictos, forms.ModelForm):
    nombre = TextoJSON(max_length=100, required=False)
    tipo = forms.ChoiceField(choices=TIPOS_VALIDOS)
    descripcion = TextoJSON()
    ataque = EnteroJSON(min_value=0, max_value=100)
    defensa = EnteroJSON(min_value=0, max_value=100)
    estamina = EnteroJSON(min_value=0, max_value=100)

    class Meta:
        model = Personaje
        fields = ['tipo', 'descripcion', 'ataque', 'defensa', 'estamina']


class PersonajeCreateForm(PersonajeForm):
    # La existencia de la referencia se resuelve en el servicio (404).
    perfil_id = EnteroJSON(min_value=1, max_value=9223372036854775807)


class HabilidadForm(CamposEstrictos, forms.ModelForm):
    nombre = TextoJSON(max_length=100)
    tipo = TextoJSON(max_length=50, required=False)
    descripcion = TextoJSON()
    incremento_ataque = EnteroJSON(min_value=-2147483648, max_value=2147483647)
    incremento_defensa = EnteroJSON(min_value=-2147483648, max_value=2147483647)
    incremento_estamina = EnteroJSON(min_value=-2147483648, max_value=2147483647)

    class Meta:
        model = Habilidad
        fields = ['nombre', 'tipo', 'descripcion', 'incremento_ataque',
                  'incremento_defensa', 'incremento_estamina']


class AsignarHabilidadForm(CamposEstrictos, forms.Form):
    habilidad_id = EnteroJSON(min_value=1, max_value=9223372036854775807)
    nivel = EnteroJSON(min_value=1, max_value=2147483647)

    def __init__(self, data, **kwargs):
        # Solo la ausencia usa el valor por defecto; null debe rechazarse.
        super().__init__({'nivel': 1, **data}, **kwargs)
