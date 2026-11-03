from django.contrib import admin

from .models import Habilidad, Perfil, Personaje, PersonajeHabilidad, RequestLog, Usuario


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


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'method', 'path', 'ip', 'called_at')
    list_filter = ('method',)
    search_fields = ('path', 'ip')
    readonly_fields = ('method', 'path', 'ip', 'called_at')

    def has_add_permission(self, request):
        return False
