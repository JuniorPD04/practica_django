import json
from ipaddress import ip_address

from .models import RequestLog


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pre-procesamiento: se persiste incluso si la vista responde 400/404/405.
        try:
            ip = str(ip_address(request.META.get('REMOTE_ADDR', '')))
        except ValueError:
            ip = None
        registro = RequestLog.objects.create(
            method=request.method, path=request.path[:255], ip=ip,
        )
        response = self.get_response(request)
        response['X-Request-Log-Id'] = str(registro.pk)
        return response


class SanitizeIdsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get('Content-Type', '').split(';', 1)[0].strip().lower()
        if (not response.streaming and not response.get('Content-Encoding')
                and (content_type == 'application/json' or content_type.endswith('+json'))):
            try:
                data = json.loads(response.content)
            except (ValueError, UnicodeDecodeError):
                return response
            response.content = json.dumps(
                self._strip_id_suffixes(data), ensure_ascii=False,
            ).encode(response.charset)
            if response.has_header('Content-Length'):
                response['Content-Length'] = str(len(response.content))
        return response

    def _strip_id_suffixes(self, data):
        if isinstance(data, dict):
            return {key: self._strip_id_suffixes(value) for key, value in data.items()
                    if not key.endswith('id')}
        if isinstance(data, list):
            return [self._strip_id_suffixes(item) for item in data]
        return data
