from django.contrib import admin

from .models import Habilidad, Perfil, Personaje, PersonajeHabilidad, Usuario


class PersonajeHabilidadInline(admin.TabularInline):
    model = PersonajeHabilidad
    extra = 1


@admin.register(Personaje)
class PersonajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'perfil', 'ataque', 'defensa', 'estamina')
    list_filter = ('tipo',)
    search_fields = ('nombre',)
    inlines = [PersonajeHabilidadInline]


admin.site.register([Usuario, Perfil, Habilidad, PersonajeHabilidad])
