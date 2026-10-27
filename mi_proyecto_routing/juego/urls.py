# juego/urls.py

from django.urls import path

from . import views


urlpatterns = [

# path('personajes/', views.personajes_list),

path('personajes/', views.personajes_list_create),

path('personajes/<int:id>/', views.personajes_detail_update_delete),

# path('personajes/', views.personaje_create) cuando el método sea POST.

# Mejor aún: usa una sola vista que despache según request.method,

# o separa por ruta y decorador como en el ejemplo.

path('habilidades/', views.habilidades_list_create),

path('habilidades/<int:id>/', views.habilidad_detail_update_delete),

# Ruta jerárquica:

path('personajes/<int:id>/habilidades/', views.habilidades_de_personaje),

# path('habilidades/<int:habilidad_id>/personajes/', views.personajes_con_habilidad),
]