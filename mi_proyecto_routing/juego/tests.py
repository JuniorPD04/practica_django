from django.contrib.auth.hashers import check_password
from django.db import IntegrityError, transaction
from django.test import Client, TestCase

from .models import Habilidad, Perfil, Personaje, PersonajeHabilidad, Usuario


class JuegoAPITests(TestCase):
    fixtures = ['datos_iniciales']

    def crear_personaje(self, **cambios):
        datos = {
            'perfil_id': 1, 'nombre': 'Prueba', 'descripcion': 'Personaje de prueba',
            'ataque': 20, 'defensa': 30, 'estamina': 40,
        }
        datos.update(cambios)
        return self.client.post('/api/personajes', datos, content_type='application/json')

    def asignar(self, personaje_id, **cambios):
        return self.client.post(
            f'/api/personajes/{personaje_id}/habilidades',
            {'habilidad_id': 1, 'nivel': 2, **cambios}, content_type='application/json',
        )

    def test_fixture_y_detalle_con_niveles_y_bonificaciones(self):
        self.assertEqual(Usuario.objects.count(), 2)
        self.assertEqual(Perfil.objects.count(), 2)
        self.assertEqual(Personaje.objects.count(), 7)
        self.assertEqual(Habilidad.objects.count(), 7)
        self.assertEqual(PersonajeHabilidad.objects.count(), 13)
        respuesta = self.client.get('/api/personajes/1')
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(datos['atributos_base'], {'ataque': 80, 'defensa': 70, 'estamina': 60})
        self.assertEqual((datos['ataque'], datos['defensa'], datos['estamina']), (90, 85, 52))
        self.assertEqual([h['nivel'] for h in datos['habilidades']], [1, 1])

    def test_listar_y_filtrar_personajes(self):
        self.assertEqual(len(self.client.get('/api/personajes').json()), 7)
        datos = self.client.get('/api/personajes?nombre=Gagh&tipo=GUERRERO').json()
        self.assertEqual([p['id'] for p in datos], [1])

    def test_personajes_se_filtran_por_usuario_a_traves_del_perfil(self):
        self.assertEqual(len(self.client.get('/api/usuarios/1/personajes').json()), 4)
        self.assertEqual(len(self.client.get('/api/usuarios/2/personajes').json()), 3)
        self.assertEqual(self.client.get('/api/usuarios/999/personajes').status_code, 404)
        usuario = Usuario.objects.create(nombre='sin_perfil', correo='otro@example.com', contrasena='demo')
        self.assertEqual(self.client.get(f'/api/usuarios/{usuario.pk}/personajes').json(), [])

    def test_crear_persiste_para_otro_cliente(self):
        respuesta = self.crear_personaje()
        self.assertEqual(respuesta.status_code, 201)
        id = respuesta.json()['id']
        self.assertTrue(Personaje.objects.filter(pk=id, perfil_id=1).exists())
        self.assertEqual(Client().get(f'/api/personajes/{id}').json()['nombre'], 'Prueba')

    def test_put_modifica_base_sin_borrar_habilidades(self):
        datos = {'nombre': 'Renombrado', 'descripcion': 'Nueva', 'ataque': 100, 'defensa': 80, 'estamina': 90}
        respuesta = self.client.put('/api/personajes/1', datos, content_type='application/json')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['ataque'], 110)
        self.assertEqual(respuesta.json()['atributos_base']['ataque'], 100)
        self.assertEqual(len(respuesta.json()['habilidades']), 2)

    def test_asignar_y_quitar_habilidad_revierte_solo_bonificacion(self):
        id = self.crear_personaje().json()['id']
        respuesta = self.asignar(id)
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()['ataque'], 40)
        self.assertEqual(respuesta.json()['estamina'], 30)
        self.assertEqual(respuesta.json()['habilidades'][0]['nivel'], 2)
        self.assertEqual(self.client.delete(f'/api/personajes/{id}/habilidades/1').status_code, 204)
        datos = self.client.get(f'/api/personajes/{id}').json()
        self.assertEqual((datos['ataque'], datos['estamina']), (20, 40))
        self.assertEqual(self.client.delete(f'/api/personajes/{id}/habilidades/1').status_code, 404)
        self.assertTrue(Habilidad.objects.filter(pk=1).exists())

    def test_nivel_por_defecto_es_uno(self):
        id = self.crear_personaje().json()['id']
        respuesta = self.client.post(f'/api/personajes/{id}/habilidades', {'habilidad_id': 1}, content_type='application/json')
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()['habilidades'][0]['nivel'], 1)

    def test_no_admite_habilidad_duplicada(self):
        self.assertEqual(self.asignar(1).status_code, 409)
        self.assertEqual(PersonajeHabilidad.objects.filter(personaje_id=1, habilidad_id=1).count(), 1)
        self.assertEqual(self.client.get('/api/personajes/1').json()['ataque'], 90)

    def test_nivel_invalido_no_crea_relacion(self):
        id = self.crear_personaje().json()['id']
        for nivel in (0, -1, True, '2', 1.5, None, 2147483648):
            with self.subTest(nivel=nivel):
                self.assertEqual(self.asignar(id, nivel=nivel).status_code, 400)
        self.assertFalse(PersonajeHabilidad.objects.filter(personaje_id=id).exists())

    def test_referencias_inexistentes(self):
        self.assertEqual(self.crear_personaje(perfil_id=999).status_code, 404)
        self.assertEqual(self.asignar(999).status_code, 404)
        self.assertEqual(self.asignar(1, habilidad_id=999).status_code, 404)
        for metodo in ('get', 'put', 'delete'):
            self.assertEqual(getattr(self.client, metodo)('/api/personajes/999').status_code, 404)

    def test_json_malformado_o_tipo_incorrecto(self):
        for datos in ('{', '[]', 'null', '"texto"', '5'):
            with self.subTest(datos=datos):
                respuesta = self.client.post('/api/personajes', datos, content_type='application/json')
                self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(self.client.post('/api/personajes', '{}', content_type='text/plain').status_code, 415)

    def test_validacion_de_campos(self):
        for cambios in ({'ataque': -1}, {'ataque': True}, {'defensa': '20'}, {'estamina': 2.5},
                        {'nombre': ''}, {'nombre': 3}, {'descripcion': None}, {'id': 55},
                        {'nombre': 'x' * 101}, {'habilidades': [1]}, {'perfil_id': True},
                        {'ataque': 2147483648}):
            with self.subTest(cambios=cambios):
                self.assertEqual(self.crear_personaje(**cambios).status_code, 400)
        self.assertEqual(self.client.post('/api/personajes', {}, content_type='application/json').status_code, 400)
        self.assertEqual(Personaje.objects.count(), 7)

    def test_borrar_personaje_elimina_pivote_y_conserva_catalogo(self):
        respuesta = self.client.delete('/api/personajes/1')
        self.assertEqual(respuesta.status_code, 204)
        self.assertEqual(respuesta.content, b'')
        self.assertFalse(PersonajeHabilidad.objects.filter(personaje_id=1).exists())
        self.assertEqual(Habilidad.objects.count(), 7)
        self.assertEqual(Perfil.objects.count(), 2)

    def test_crud_habilidades_y_recalculo_al_editar_o_borrar(self):
        datos = {'nombre': 'Aura', 'descripcion': 'Protege', 'incremento_ataque': 3,
                 'incremento_defensa': 4, 'incremento_estamina': -2}
        respuesta = self.client.post('/api/habilidades', datos, content_type='application/json')
        self.assertEqual(respuesta.status_code, 201)
        id = respuesta.json()['id']
        self.assertEqual(self.asignar(1, habilidad_id=id).status_code, 201)
        self.assertEqual(self.client.get('/api/personajes/1').json()['ataque'], 96)
        datos['incremento_ataque'] = 8
        self.assertEqual(self.client.put(f'/api/habilidades/{id}', datos, content_type='application/json').status_code, 200)
        self.assertEqual(self.client.get('/api/personajes/1').json()['ataque'], 106)
        self.assertEqual(self.client.get(f'/api/habilidades/{id}').json()['nombre'], 'Aura')
        self.assertEqual(self.client.delete(f'/api/habilidades/{id}').status_code, 204)
        self.assertEqual(self.client.get('/api/personajes/1').json()['ataque'], 90)
        self.assertEqual(self.client.get(f'/api/habilidades/{id}').status_code, 404)

    def test_filtro_y_orden_habilidades(self):
        habilidades = self.client.get('/api/habilidades?orden=estamina').json()
        valores = [h['incremento_estamina'] for h in habilidades]
        self.assertEqual(valores, sorted(valores, reverse=True))
        self.assertEqual(len(self.client.get('/api/habilidades?nombre=Espadazo').json()), 1)
        Habilidad.objects.filter(pk=1).update(tipo='combate')
        self.assertEqual(len(self.client.get('/api/habilidades?tipo=COMBATE').json()), 1)

    def test_rutas_con_barra_y_sin_barra(self):
        for ruta in ('/api/personajes', '/api/personajes/1', '/api/usuarios',
                     '/api/usuarios/1/personajes', '/api/personajes/1/habilidades',
                     '/api/habilidades', '/api/habilidades/1'):
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).json(), self.client.get(ruta + '/').json())
        datos = {'perfil_id': 1, 'nombre': 'Barra', 'descripcion': 'Prueba', 'ataque': 1, 'defensa': 1, 'estamina': 1}
        self.assertEqual(self.client.post('/api/personajes/', datos, content_type='application/json').status_code, 201)

    def test_metodos_no_permitidos(self):
        respuesta = self.client.patch('/api/personajes/1', '{}', content_type='application/json')
        self.assertEqual(respuesta.status_code, 405)
        self.assertIn('PUT', respuesta['Allow'])
        self.assertIn('error', respuesta.json())

    def test_usuarios_no_exponen_contrasenas(self):
        self.assertNotIn('contrasena', self.client.get('/api/usuarios').json()[0])
        self.assertTrue(check_password('JuegoDemo2026!', Usuario.objects.get(pk=1).contrasena))
        usuario = Usuario.objects.create(nombre='nuevo', correo='nuevo@example.com', contrasena='secreto')
        self.assertTrue(check_password('secreto', usuario.contrasena))
        anterior = usuario.contrasena
        usuario.save()
        self.assertEqual(usuario.contrasena, anterior)

    def test_restricciones_reales_en_base_de_datos(self):
        for datos in ({'personaje_id': 1, 'habilidad_id': 1, 'nivel': 2},
                      {'personaje_id': 1, 'habilidad_id': 3, 'nivel': 0}):
            with self.subTest(datos=datos), self.assertRaises(IntegrityError), transaction.atomic():
                PersonajeHabilidad.objects.create(**datos)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Perfil.objects.create(usuario_id=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Usuario.objects.create(nombre='otro', correo=Usuario.objects.get(pk=1).correo, contrasena='demo')

    def test_relaciones_inversas_y_cascada_usuario(self):
        usuario = Usuario.objects.get(pk=1)
        self.assertEqual(usuario.perfil.personajes.count(), 4)
        self.assertEqual(Habilidad.objects.get(pk=1).personajes.count(), 2)
        usuario.delete()
        self.assertEqual(Personaje.objects.count(), 3)
        self.assertEqual(Perfil.objects.count(), 1)
        self.assertEqual(Habilidad.objects.count(), 7)
