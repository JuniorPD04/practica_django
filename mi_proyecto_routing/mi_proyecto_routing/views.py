import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_safe


@require_safe
def authors(request):
    """Verificación pública del equipo; no requiere JWT."""
    integrantes = json.loads((settings.BASE_DIR / 'authors.json').read_text(encoding='utf-8'))
    return JsonResponse(integrantes, safe=False, json_dumps_params={'ensure_ascii': False})
