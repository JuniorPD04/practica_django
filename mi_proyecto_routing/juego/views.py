"""API JSON del juego. Todas las lecturas y escrituras usan el ORM."""

import json
from functools import wraps

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Habilidad, Perfil, Personaje, PersonajeHabilidad, Usuario
from .serializers import habilidad_json, personaje_json


class ErrorAPI(Exception):
    def __init__(self, mensaje, status=400):
        self.mensaje = mensaje
        self.status = status


def api(metodos):
    """Errores previsibles en JSON y control de métodos para clientes como Postman."""
    def decorar(vista):
        @csrf_exempt
        @wraps(vista)
        def responder(request, *args, **kwargs):
            if request.method not in metodos:
                respuesta = JsonResponse({'error': 'Método no permitido'}, status=405)
                respuesta['Allow'] = ', '.join(metodos)
                return respuesta
            try:
                return vista(request, *args, **kwargs)
            except ErrorAPI as error:
                return JsonResponse({'error': error.mensaje}, status=error.status)
            except ValidationError as error:
                detalles = error.message_dict if hasattr(error, 'message_dict') else error.messages
                return JsonResponse({'error': 'Datos inválidos', 'detalles': detalles}, status=400)
        return responder
    return decorar


def obtener(modelo, id):
    objeto = modelo.objects.filter(pk=id).first()
    if objeto is None:
        raise ErrorAPI(f'{modelo.__name__} no encontrado', 404)
    return objeto


def cuerpo(request, requeridos, opcionales=()):
    if request.content_type != 'application/json':
        raise ErrorAPI('Usa Content-Type: application/json', 415)
    try:
        datos = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        raise ErrorAPI('El cuerpo debe ser JSON válido')
    if not isinstance(datos, dict):
        raise ErrorAPI('El cuerpo debe ser un objeto JSON')
    faltantes = set(requeridos) - datos.keys()
    desconocidos = datos.keys() - set(requeridos) - set(opcionales)
    if faltantes or desconocidos:
        raise ErrorAPI({'faltantes': sorted(faltantes), 'desconocidos': sorted(desconocidos)})
    return datos


def entero(valor, nombre, minimo=None):
    if type(valor) is not int or (minimo is not None and valor < minimo):
        mensaje = f'{nombre} debe ser un entero'
        if minimo is not None:
            mensaje += f' mayor o igual a {minimo}'
        raise ErrorAPI(mensaje)
    return valor


def guardar(objeto, datos):
    for nombre, valor in datos.items():
        campo = objeto._meta.get_field(nombre)
        if isinstance(campo, models.IntegerField):
            entero(valor, nombre)
            minimo = 0 if isinstance(campo, models.PositiveIntegerField) else -2147483648
            if not minimo <= valor <= 2147483647:
                raise ErrorAPI(f'{nombre} debe estar entre {minimo} y 2147483647')
        elif not isinstance(valor, str):
            raise ErrorAPI(f'{nombre} debe ser texto')
        setattr(objeto, nombre, valor)
    objeto.full_clean()
    objeto.save()
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


CAMPOS_PERSONAJE = ('nombre', 'descripcion', 'ataque', 'defensa', 'estamina')
CAMPOS_HABILIDAD = (
    'nombre', 'descripcion', 'incremento_ataque', 'incremento_defensa', 'incremento_estamina',
)


@api(['GET', 'POST'])
def personajes_list_create(request):
    if request.method == 'GET':
        personajes = personajes_query()
        if request.GET.get('nombre'):
            personajes = personajes.filter(nombre__icontains=request.GET['nombre'])
        if request.GET.get('tipo'):
            personajes = personajes.filter(tipo__iexact=request.GET['tipo'])
        return JsonResponse([personaje_json(p) for p in personajes], safe=False)
    datos = cuerpo(request, (*CAMPOS_PERSONAJE, 'perfil_id'), ('tipo',))
    perfil = obtener(Perfil, entero(datos.pop('perfil_id'), 'perfil_id', 1))
    personaje = guardar(Personaje(perfil=perfil), datos)
    return JsonResponse(detalle_personaje(personaje.pk), status=201)


@api(['GET', 'PUT', 'DELETE'])
def personajes_detail_update_delete(request, id):
    if request.method == 'GET':
        return JsonResponse(detalle_personaje(id))
    personaje = obtener(Personaje, id)
    if request.method == 'DELETE':
        personaje.delete()
        return HttpResponse(status=204)
    # PUT escribe atributos base; las bonificaciones se calculan al responder.
    guardar(personaje, cuerpo(request, CAMPOS_PERSONAJE, ('tipo',)))
    return JsonResponse(detalle_personaje(id))


@api(['GET'])
def usuarios_list(request):
    # Nunca exponemos el hash de la contraseña.
    return JsonResponse(list(Usuario.objects.order_by('id').values('id', 'nombre', 'correo')), safe=False)


@api(['GET'])
def personajes_de_usuario(request, id):
    usuario = obtener(Usuario, id)
    personajes = personajes_query().filter(perfil__usuario=usuario)
    return JsonResponse([personaje_json(p) for p in personajes], safe=False)


@api(['GET', 'POST'])
def habilidades_de_personaje(request, id):
    obtener(Personaje, id)
    if request.method == 'GET':
        return JsonResponse(detalle_personaje(id)['habilidades'], safe=False)
    datos = cuerpo(request, ('habilidad_id',), ('nivel',))
    habilidad = obtener(Habilidad, entero(datos['habilidad_id'], 'habilidad_id', 1))
    nivel = entero(datos.get('nivel', 1), 'nivel', 1)
    if nivel > 2147483647:
        raise ErrorAPI('nivel supera el máximo permitido: 2147483647')
    with transaction.atomic():
        _, creada = PersonajeHabilidad.objects.get_or_create(
            personaje_id=id, habilidad=habilidad, defaults={'nivel': nivel},
        )
        if not creada:
            raise ErrorAPI('El personaje ya posee esta habilidad', 409)
    return JsonResponse(detalle_personaje(id), status=201)


@api(['DELETE'])
def quitar_habilidad(request, id, habilidad_id):
    obtener(Personaje, id)
    relacion = PersonajeHabilidad.objects.filter(personaje_id=id, habilidad_id=habilidad_id)
    if not relacion.exists():
        raise ErrorAPI('El personaje no posee esta habilidad', 404)
    relacion.delete()
    return HttpResponse(status=204)


@api(['GET', 'POST'])
def habilidades_list_create(request):
    if request.method == 'POST':
        habilidad = guardar(Habilidad(), cuerpo(request, CAMPOS_HABILIDAD, ('tipo',)))
        return JsonResponse(habilidad_json(habilidad), status=201)
    habilidades = Habilidad.objects.order_by('id')
    if request.GET.get('nombre'):
        habilidades = habilidades.filter(nombre__icontains=request.GET['nombre'])
    if request.GET.get('tipo'):
        habilidades = habilidades.filter(tipo__iexact=request.GET['tipo'])
    if request.GET.get('orden') == 'estamina':
        habilidades = habilidades.order_by('-incremento_estamina', 'id')
    return JsonResponse([habilidad_json(h) for h in habilidades], safe=False)


@api(['GET', 'PUT', 'DELETE'])
def habilidad_detail_update_delete(request, id):
    habilidad = obtener(Habilidad, id)
    if request.method == 'DELETE':
        habilidad.delete()
        return HttpResponse(status=204)
    if request.method == 'PUT':
        guardar(habilidad, cuerpo(request, CAMPOS_HABILIDAD, ('tipo',)))
    return JsonResponse(habilidad_json(habilidad))
