"""Consultas y operaciones de negocio, independientes de las respuestas HTTP."""

from django.db import transaction
from django.db.models import Prefetch

from .exceptions import ErrorAPI
from .models import Habilidad, Perfil, Personaje, PersonajeHabilidad
from .serializers import personaje_json


def obtener(modelo, id):
    objeto = modelo.objects.filter(pk=id).first()
    if objeto is None:
        raise ErrorAPI(f'{modelo.__name__} no encontrado', 404)
    return objeto


def personajes_query():
    return Personaje.objects.prefetch_related(Prefetch(
        'habilidades_adquiridas',
        queryset=PersonajeHabilidad.objects.select_related('habilidad').order_by('habilidad_id'),
    )).order_by('id')


def detalle_personaje(id):
    personaje = personajes_query().filter(pk=id).first()
    if personaje is None:
        raise ErrorAPI('Personaje no encontrado', 404)
    return personaje_json(personaje)


def crear_personaje(form):
    perfil = obtener(Perfil, form.cleaned_data['perfil_id'])
    personaje = form.save(commit=False)
    personaje.perfil = perfil
    personaje.save()
    return personaje


def asignar_habilidad(personaje, datos):
    habilidad = obtener(Habilidad, datos['habilidad_id'])
    with transaction.atomic():
        _, creada = PersonajeHabilidad.objects.get_or_create(
            personaje=personaje, habilidad=habilidad, defaults={'nivel': datos['nivel']},
        )
        if not creada:
            raise ErrorAPI('El personaje ya posee esta habilidad', 409)


def retirar_habilidad(id, habilidad_id):
    obtener(Personaje, id)
    relacion = PersonajeHabilidad.objects.filter(personaje_id=id, habilidad_id=habilidad_id)
    if not relacion.exists():
        raise ErrorAPI('El personaje no posee esta habilidad', 404)
    relacion.delete()
