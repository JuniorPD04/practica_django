import json

from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from .middleware import RequestLoggingMiddleware, SanitizeIdsMiddleware
from .models import Habilidad, Personaje, PersonajeHabilidad, RequestLog
from .serializers import personaje_json
from .services import personajes_query


class ValidatorsTests(TestCase):
    fixtures = ['datos_iniciales']

    def setUp(self):
        self.personaje = {
            'perfil_id': 1, 'nombre': 'Prueba', 'tipo': 'guerrero', 'descripcion': 'Ejemplo',
            'ataque': 20, 'defensa': 30, 'estamina': 40,
        }
        self.habilidad = {
            'nombre': 'Aura', 'descripcion': 'Prueba', 'incremento_ataque': 3,
            'incremento_defensa': 4, 'incremento_estamina': -2,
        }

    def test_personaje_requiere_tipo_y_valida_eleccion_y_limites(self):
        for campo, valor in [('tipo', 'dragon'), ('tipo', None), ('ataque', 101),
                             ('defensa', -1), ('estamina', 100.5)]:
            with self.subTest(campo=campo, valor=valor):
                respuesta = self.client.post('/api/personajes', {**self.personaje, campo: valor},
                                             content_type='application/json')
                self.assertEqual(respuesta.status_code, 400)
                self.assertIn(campo, [e['field'] for e in respuesta.json()['errors']])
        del self.personaje['tipo']
        respuesta = self.client.post('/api/personajes', self.personaje, content_type='application/json')
        self.assertIn('tipo', [e['field'] for e in respuesta.json()['errors']])
        self.assertEqual(Personaje.objects.count(), 7)

    def test_personaje_admite_extremos_y_tipos_del_fixture(self):
        for tipo in ('guerrero', 'maga', 'elfo', 'asesino', 'enano', 'arquera', 'orco'):
            respuesta = self.client.post('/api/personajes', {
                **self.personaje, 'tipo': tipo, 'ataque': 0, 'defensa': 100,
            }, content_type='application/json')
            self.assertEqual(respuesta.status_code, 201)

    def test_put_invalido_no_cambia_personaje_ni_relaciones(self):
        original = Personaje.objects.get(pk=1)
        datos = {k: v for k, v in self.personaje.items() if k != 'perfil_id'}
        for cambios in ({'ataque': 101}, {'tipo': 'dragon'}, {'defensa': True}, {'perfil_id': 2}):
            with self.subTest(cambios=cambios):
                respuesta = self.client.put('/api/personajes/1', {**datos, **cambios},
                                            content_type='application/json')
                self.assertEqual(respuesta.status_code, 400)
                actual = Personaje.objects.get(pk=1)
                self.assertEqual(actual.nombre, original.nombre)
                self.assertEqual(actual.ataque, original.ataque)
                self.assertEqual(actual.perfil_id, original.perfil_id)
        self.assertEqual(PersonajeHabilidad.objects.filter(personaje_id=1).count(), 2)

    def test_habilidad_post_y_put_rechazan_campos_invalidos_sin_guardar(self):
        original = Habilidad.objects.get(pk=1)
        for metodo, ruta in [('post', '/api/habilidades'), ('put', '/api/habilidades/1')]:
            for cambios in ({'nombre': 42}, {'descripcion': None}, {'incremento_ataque': True},
                            {'incremento_defensa': '2'}, {'incremento_estamina': 2147483648},
                            {'incremento_estamina': -2147483649}, {'extra': 'ignorar'}):
                with self.subTest(metodo=metodo, cambios=cambios):
                    respuesta = getattr(self.client, metodo)(ruta, {**self.habilidad, **cambios},
                                                             content_type='application/json')
                    self.assertEqual(respuesta.status_code, 400)
                    self.assertTrue(respuesta.json()['errors'])
            respuesta = getattr(self.client, metodo)(ruta, {}, content_type='application/json')
            self.assertIn('nombre', [e['field'] for e in respuesta.json()['errors']])
        self.assertEqual(Habilidad.objects.count(), 7)
        self.assertEqual(Habilidad.objects.get(pk=1).nombre, original.nombre)

    def test_asignacion_invalida_da_errores_por_campo_y_no_crea_relacion(self):
        for datos, campo in [({}, 'habilidad_id'), ({'habilidad_id': '3'}, 'habilidad_id'),
                             ({'habilidad_id': 3, 'nivel': None}, 'nivel'),
                             ({'habilidad_id': 3, 'nivel': 0}, 'nivel')]:
            respuesta = self.client.post('/api/personajes/1/habilidades', datos,
                                         content_type='application/json')
            self.assertEqual(respuesta.status_code, 400)
            self.assertIn(campo, [e['field'] for e in respuesta.json()['errors']])
        self.assertFalse(PersonajeHabilidad.objects.filter(personaje_id=1, habilidad_id=3).exists())

    def test_sanitizacion_real_elimina_fk_y_conserva_id_y_payload(self):
        bruto = personaje_json(personajes_query().get(pk=1))
        self.assertIn('perfil_id', bruto)
        limpio = self.client.get('/api/personajes/1').json()
        self.assertEqual(limpio, {k: v for k, v in bruto.items() if k != 'perfil_id'})


class LoggingTests(TestCase):
    fixtures = ['datos_iniciales']

    def test_registro_ocurre_antes_del_controlador(self):
        request = RequestFactory().get('/demo?secreto=no-guardar', REMOTE_ADDR='::1')

        def vista(request):
            log = RequestLog.objects.get()
            self.assertEqual((log.method, log.path, log.ip), ('GET', '/demo', '::1'))
            return JsonResponse({'ok': True})

        response = RequestLoggingMiddleware(vista)(request)
        self.assertEqual(response['X-Request-Log-Id'], str(RequestLog.objects.get().pk))

    def test_cada_metodo_y_errores_dejan_exactamente_un_registro(self):
        for metodo, ruta, datos in [('get', '/api/personajes', None),
                                    ('post', '/api/personajes', {}),
                                    ('put', '/api/personajes/1', {}),
                                    ('delete', '/api/personajes/1', None),
                                    ('get', '/no-existe', None),
                                    ('patch', '/api/habilidades', {})]:
            antes = RequestLog.objects.count()
            kwargs = {'data': datos, 'content_type': 'application/json'} if datos is not None else {}
            response = getattr(self.client, metodo)(ruta, **kwargs)
            self.assertEqual(RequestLog.objects.count(), antes + 1)
            log = RequestLog.objects.get(pk=response['X-Request-Log-Id'])
            self.assertEqual((log.method, log.path), (metodo.upper(), ruta))
            self.assertIsNotNone(log.called_at)

    def test_ip_ausente_o_invalida_no_rompe_peticion(self):
        for ip in ('', 'invalid', '2001:db8::1'):
            respuesta = self.client.get('/api/usuarios', REMOTE_ADDR=ip)
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(RequestLog.objects.latest('id').ip, ip if ':' in ip else None)

    @override_settings(DEBUG=True)
    def test_consulta_logs_demuestra_persistencia_y_tambien_se_registra(self):
        response = self.client.get('/api/personajes')
        log_id = int(response['X-Request-Log-Id'])
        logs = self.client.get('/api/request-logs').json()
        log = next(item for item in logs if item['id'] == log_id)
        self.assertEqual(log['path'], '/api/personajes')
        self.assertEqual(logs[0]['path'], '/api/request-logs')

    @override_settings(DEBUG=False)
    def test_consulta_logs_no_disponible_fuera_de_desarrollo(self):
        self.assertEqual(self.client.get('/api/request-logs').status_code, 404)


class SanitizationTests(SimpleTestCase):
    def aplicar(self, response):
        return SanitizeIdsMiddleware(lambda request: response)(RequestFactory().get('/'))

    def test_recursion_y_preservacion_de_otros_campos(self):
        datos = {'id': 8, 'perfil_id': 1, '_id': 'interno', 'nombre': 'Maga ágil',
                 'anidado': {'usuario_id': 9, 'id': 2, 'valido': True},
                 'lista': [{'habilidad_id': 3, 'nivel': 2}, [None, 4, {'otro_id': 5}]]}
        response = JsonResponse(datos)
        response['Content-Length'] = str(len(response.content))
        response = self.aplicar(response)
        self.assertEqual(json.loads(response.content), {
            'id': 8, 'nombre': 'Maga ágil', 'anidado': {'id': 2, 'valido': True},
            'lista': [{'nivel': 2}, [None, 4, {}]],
        })
        self.assertEqual(int(response['Content-Length']), len(response.content))

    def test_sanitiza_listas_y_errores_json(self):
        response = self.aplicar(JsonResponse([{'perfil_id': 1, 'id': 2}], safe=False))
        self.assertEqual(json.loads(response.content), [{'id': 2}])
        response = self.aplicar(JsonResponse({'errors': {'perfil_id': ['Inválido'], 'nombre': ['Falta']}}, status=400))
        self.assertEqual(json.loads(response.content), {'errors': {'nombre': ['Falta']}})
        self.assertEqual(response.status_code, 400)

    def test_omite_no_json_json_invalido_streaming_y_204(self):
        for response in (HttpResponse('<html>perfil_id</html>'), HttpResponse(status=204),
                         HttpResponse('{', content_type='application/json')):
            anterior = response.content
            self.assertEqual(self.aplicar(response).content, anterior)
        response = StreamingHttpResponse(iter([b'{"perfil_id": 1}']), content_type='application/json')
        self.assertIs(self.aplicar(response), response)
        response.close()
