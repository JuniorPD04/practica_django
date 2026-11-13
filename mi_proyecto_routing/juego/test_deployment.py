import json
import os
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Personaje, UserProfile


class DeploymentTests(TestCase):
    def test_authors_publico_sin_token_y_con_codigos_exactos(self):
        expected = json.loads((settings.BASE_DIR / 'authors.json').read_text(encoding='utf-8'))
        for path in ('/authors', '/authors/'):
            response = self.client.get(path, HTTP_AUTHORIZATION='Bearer token-invalido')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected)
        self.assertEqual([a['codigo'] for a in expected], ['407721', '407719', '385387'])

    @override_settings(DEBUG=False, SECURE_SSL_REDIRECT=True, ALLOWED_HOSTS=['routing-api.onrender.com'])
    def test_proxy_https_y_hosts_de_produccion(self):
        response = self.client.get('/authors', HTTP_HOST='routing-api.onrender.com',
                                   HTTP_X_FORWARDED_PROTO='https')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/authors', HTTP_HOST='routing-api.onrender.com').status_code, 301)
        self.assertEqual(self.client.get('/authors', HTTP_HOST='intruso.example', secure=True).status_code, 400)

    def test_inicializacion_no_restaura_datos_ni_contrasenas(self):
        env = {'LOAD_DEMO_DATA': 'True', 'DJANGO_SUPERUSER_USERNAME': 'admin-prueba',
               'DJANGO_SUPERUSER_PASSWORD': 'ClaveTemporalSoloParaTest123!',
               'DJANGO_SUPERUSER_EMAIL': 'admin@example.com'}
        with patch.dict(os.environ, env):
            call_command('initialize_deployment', verbosity=0)
            user = get_user_model().objects.get(username='admin-prueba')
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.check_password(env['DJANGO_SUPERUSER_PASSWORD']))
            self.assertEqual(UserProfile.objects.get(user=user).role, 'ADMIN')
            response = self.client.post('/api/login/', {
                'username': 'admin-prueba', 'password': env['DJANGO_SUPERUSER_PASSWORD'],
            }, content_type='application/json')
            self.assertEqual(response.status_code, 200)
            token = response.json()['access']
            response = self.client.get('/api/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['role'], 'ADMIN')
            self.assertEqual(self.client.get('/api/usuarios/',
                HTTP_AUTHORIZATION=f'Bearer {token}').status_code, 200)
            self.assertEqual(Personaje.objects.count(), 7)
            Personaje.objects.filter(pk=1).update(nombre='Editado en producción')
            user.set_password('NuevaClave123!')
            user.save()
            call_command('initialize_deployment', verbosity=0)
            user.refresh_from_db()
            self.assertTrue(user.check_password('NuevaClave123!'))
            self.assertEqual(Personaje.objects.get(pk=1).nombre, 'Editado en producción')
