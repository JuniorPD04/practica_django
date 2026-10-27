"""Conversión explícita de modelos a JSON, sin dependencias adicionales."""

ATRIBUTOS = ('ataque', 'defensa', 'estamina')


def habilidad_json(habilidad):
    return {
        'id': habilidad.pk, 'nombre': habilidad.nombre, 'tipo': habilidad.tipo,
        'descripcion': habilidad.descripcion,
        **{f'incremento_{a}': getattr(habilidad, f'incremento_{a}') for a in ATRIBUTOS},
    }


def personaje_json(personaje):
    base = {a: getattr(personaje, a) for a in ATRIBUTOS}
    efectivos = base.copy()
    habilidades = []
    for relacion in personaje.habilidades_adquiridas.all():
        habilidad = relacion.habilidad
        habilidades.append({**habilidad_json(habilidad), 'nivel': relacion.nivel})
        for atributo in ATRIBUTOS:
            efectivos[atributo] += getattr(habilidad, f'incremento_{atributo}') * relacion.nivel
    return {
        'id': personaje.pk, 'perfil_id': personaje.perfil_id,
        'nombre': personaje.nombre, 'tipo': personaje.tipo,
        'descripcion': personaje.descripcion, **efectivos,
        'atributos_base': base, 'habilidades': habilidades,
    }
