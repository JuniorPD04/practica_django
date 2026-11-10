"""Controladores organizados por recurso."""

from .habilidades import habilidad_detail_update_delete, habilidades_list_create
from .personajes import (
    habilidades_de_personaje, personajes_detail_update_delete,
    personajes_list_create, quitar_habilidad,
)
from .usuarios import personajes_de_usuario, usuarios_list
from .logs import request_logs
from .autenticador import me