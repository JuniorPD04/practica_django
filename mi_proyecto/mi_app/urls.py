from django.urls import path

from .views import clasificacion_edad, contador_vocales, hola_mundo, libros, pasar_kilo_a_libra, frutas


urlpatterns = [
    path('hola/', hola_mundo),
    path('kilos/', pasar_kilo_a_libra),
    path('clasificacion_edad/', clasificacion_edad),
    path('contador_vocales/', contador_vocales),
    path('libros/', libros),
    path('frutas/', frutas),
]