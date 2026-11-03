"""Adaptación HTTP común; las reglas de entrada viven en forms.py."""

import json
from functools import wraps

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .exceptions import ErrorAPI


def api(metodos):
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
                # Los nombres de campos son valores: el post-filter no elimina
                # errores de perfil_id/habilidad_id por terminar su clave en _id.
                errores = ([{'field': campo, 'messages': mensajes}
                            for campo, mensajes in detalles.items()]
                           if isinstance(detalles, dict)
                           else [{'field': '__all__', 'messages': detalles}])
                return JsonResponse({'error': 'Datos inválidos', 'errors': errores}, status=400)
        return responder
    return decorar


def validar(request, clase_form, **kwargs):
    if request.content_type != 'application/json':
        raise ErrorAPI('Usa Content-Type: application/json', 415)
    try:
        datos = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        raise ValidationError({'__all__': ['El cuerpo debe ser JSON válido']})
    if not isinstance(datos, dict):
        raise ValidationError({'__all__': ['El cuerpo debe ser un objeto JSON']})
    form = clase_form(datos, **kwargs)
    if not form.is_valid():
        raise ValidationError(dict(form.errors))
    return form
