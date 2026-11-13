from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decouple import AutoConfig

from juego.models import Habilidad, Perfil, Personaje, PersonajeHabilidad, Usuario, UserProfile


class Command(BaseCommand):
    help = 'Inicializa una BD nueva sin sobrescribir datos ni contraseñas en redespliegues.'

    @transaction.atomic
    def handle(self, *args, **options):
        config = AutoConfig(search_path=settings.BASE_DIR)
        username = config('DJANGO_SUPERUSER_USERNAME', default='')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='')
        email = config('DJANGO_SUPERUSER_EMAIL', default='')
        if bool(username) != bool(password):
            raise CommandError('Configura usuario y contraseña iniciales juntos, o deja ambos vacíos.')
        if username:
            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_superuser(username=username, email=email, password=password)
                UserProfile.objects.create(user=user, role='ADMIN')
                self.stdout.write(self.style.SUCCESS('Cuenta inicial creada con rol ADMIN.'))
            else:
                self.stdout.write('La cuenta inicial ya existe; no se modifica.')

        if config('LOAD_DEMO_DATA', default=False, cast=bool):
            models = (Usuario, Perfil, Habilidad, Personaje, PersonajeHabilidad)
            if not any(model.objects.exists() for model in models):
                call_command('loaddata', 'datos_iniciales', verbosity=0)
                self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados en la BD vacía.'))
            else:
                self.stdout.write('Ya existen datos del juego; no se carga el fixture.')
