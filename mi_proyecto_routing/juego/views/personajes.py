from django.http import HttpResponse, JsonResponse

from ..api import api, validar
from ..forms import AsignarHabilidadForm, PersonajeCreateForm, PersonajeForm
from ..models import Personaje
from ..serializers import personaje_json
from ..services import (
    asignar_habilidad, crear_personaje, detalle_personaje, obtener,
    personajes_query, retirar_habilidad,
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
    personaje = crear_personaje(validar(request, PersonajeCreateForm))
    return JsonResponse(detalle_personaje(personaje.pk), status=201)


@api(['GET', 'PUT', 'DELETE'])
def personajes_detail_update_delete(request, id):
    if request.method == 'GET':
        return JsonResponse(detalle_personaje(id))
    personaje = obtener(Personaje, id)
    if request.method == 'DELETE':
        personaje.delete()
        return HttpResponse(status=204)
    validar(request, PersonajeForm, instance=personaje).save()
    return JsonResponse(detalle_personaje(id))


@api(['GET', 'POST'])
def habilidades_de_personaje(request, id):
    personaje = obtener(Personaje, id)
    if request.method == 'GET':
        return JsonResponse(detalle_personaje(id)['habilidades'], safe=False)
    asignar_habilidad(personaje, validar(request, AsignarHabilidadForm).cleaned_data)
    return JsonResponse(detalle_personaje(id), status=201)


@api(['DELETE'])
def quitar_habilidad(request, id, habilidad_id):
    retirar_habilidad(id, habilidad_id)
    return HttpResponse(status=204)
