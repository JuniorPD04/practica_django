from django.http import JsonResponse

from ..api import api
from ..models import Usuario
from ..serializers import personaje_json
from ..services import obtener, personajes_query


@api(['GET'])
def usuarios_list(request):
    return JsonResponse(list(Usuario.objects.order_by('id').values('id', 'nombre', 'correo')), safe=False)


@api(['GET'])
def personajes_de_usuario(request, id):
    usuario = obtener(Usuario, id)
    return JsonResponse([
        personaje_json(p) for p in personajes_query().filter(perfil__usuario=usuario)
    ], safe=False)
