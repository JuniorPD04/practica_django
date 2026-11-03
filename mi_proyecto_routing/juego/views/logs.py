from django.conf import settings
from django.http import JsonResponse

from ..api import ErrorAPI, api
from ..models import RequestLog


@api(['GET'])
def request_logs(request):
    """Evidencia de la actividad en desarrollo; no se expone fuera de DEBUG."""
    if not settings.DEBUG:
        raise ErrorAPI('Recurso no encontrado', 404)
    registros = RequestLog.objects.order_by('-id')[:100]
    return JsonResponse(list(registros.values('id', 'method', 'path', 'ip', 'called_at')), safe=False)
