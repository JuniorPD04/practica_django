from django.http import HttpResponse, JsonResponse

from ..api import api, validar
from ..forms import HabilidadForm
from ..models import Habilidad
from ..serializers import habilidad_json
from ..services import obtener


@api(['GET', 'POST'])
def habilidades_list_create(request):
    if request.method == 'POST':
        habilidad = validar(request, HabilidadForm).save()
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
        habilidad = validar(request, HabilidadForm, instance=habilidad).save()
    return JsonResponse(habilidad_json(habilidad))
