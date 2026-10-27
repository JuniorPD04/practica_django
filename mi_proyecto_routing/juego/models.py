from django.core.validators import MinValueValidator
from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import models


class Usuario(models.Model):
    # Usuario del juego, independiente del usuario de autenticación de Django.
    nombre = models.CharField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=128)
    correo = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        # También protege las contraseñas introducidas desde el administrador.
        try:
            identify_hasher(self.contrasena)
        except ValueError:
            self.contrasena = make_password(self.contrasena)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil')
    biografia = models.TextField(blank=True)
    avatar = models.URLField(blank=True)

    def __str__(self):
        return f'Perfil de {self.usuario.nombre}'


class Habilidad(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField()
    incremento_ataque = models.IntegerField(default=0)
    incremento_defensa = models.IntegerField(default=0)
    incremento_estamina = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


class Personaje(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='personajes')
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField()
    # Atributos base; los efectivos incluyen las habilidades y sus niveles.
    ataque = models.PositiveIntegerField()
    defensa = models.PositiveIntegerField()
    estamina = models.PositiveIntegerField()
    habilidades = models.ManyToManyField(
        Habilidad, through='PersonajeHabilidad', related_name='personajes', blank=True,
    )

    def __str__(self):
        return self.nombre


class PersonajeHabilidad(models.Model):
    personaje = models.ForeignKey(
        Personaje, on_delete=models.CASCADE, related_name='habilidades_adquiridas',
    )
    habilidad = models.ForeignKey(
        Habilidad, on_delete=models.CASCADE, related_name='adquisiciones',
    )
    nivel = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['personaje', 'habilidad'], name='personaje_habilidad_unica'),
            models.CheckConstraint(condition=models.Q(nivel__gte=1), name='nivel_minimo_uno'),
        ]

    def __str__(self):
        return f'{self.personaje} / {self.habilidad} (nivel {self.nivel})'
