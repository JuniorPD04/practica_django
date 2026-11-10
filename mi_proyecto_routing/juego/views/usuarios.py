from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..api import api
from ..models import Usuario
from ..serializers import personaje_json
from ..services import obtener, personajes_query
from juego.permissions import IsAdmin

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def usuarios_list(request):
    return JsonResponse(list(Usuario.objects.order_by('id').values('id', 'nombre', 'correo')), safe=False)


@api_view(['GET'])
def personajes_de_usuario(request, id):
    usuario = obtener(Usuario, id)
    return JsonResponse([
        personaje_json(p) for p in personajes_query().filter(perfil__usuario=usuario)
    ], safe=False)
