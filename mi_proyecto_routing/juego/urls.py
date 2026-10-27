from django.urls import path

from . import views


# Ambas variantes funcionan sin redirigir los cuerpos de POST/PUT.
rutas = [
    ('usuarios', views.usuarios_list, 'usuarios'),
    ('usuarios/<int:id>/personajes', views.personajes_de_usuario, 'personajes-usuario'),
    ('personajes', views.personajes_list_create, 'personajes'),
    ('personajes/<int:id>', views.personajes_detail_update_delete, 'personaje'),
    ('personajes/<int:id>/habilidades', views.habilidades_de_personaje, 'personaje-habilidades'),
    ('personajes/<int:id>/habilidades/<int:habilidad_id>', views.quitar_habilidad, 'quitar-habilidad'),
    ('habilidades', views.habilidades_list_create, 'habilidades'),
    ('habilidades/<int:id>', views.habilidad_detail_update_delete, 'habilidad'),
]

urlpatterns = []
for ruta, vista, nombre in rutas:
    urlpatterns.append(path(ruta, vista, name=nombre))
    urlpatterns.append(path(ruta + '/', vista))
