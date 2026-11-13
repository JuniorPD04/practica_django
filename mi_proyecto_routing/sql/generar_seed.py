"""Regenera seed.sql desde el fixture oficial, sin conectarse a una base de datos."""
import json
from pathlib import Path


TABLES = {
    'usuario': ['nombre', 'contrasena', 'correo'],
    'perfil': ['usuario_id', 'biografia', 'avatar'],
    'habilidad': ['nombre', 'tipo', 'descripcion', 'incremento_ataque',
                  'incremento_defensa', 'incremento_estamina'],
    'personaje': ['perfil_id', 'nombre', 'tipo', 'descripcion', 'ataque', 'defensa', 'estamina'],
    'personajehabilidad': ['personaje_id', 'habilidad_id', 'nivel'],
}


def literal(value):
    if value is None:
        return 'NULL'
    if isinstance(value, int):
        return str(value)
    return "'" + value.replace("'", "''") + "'"


def main():
    folder = Path(__file__).resolve().parent
    fixture = json.loads((folder.parent / 'juego/fixtures/datos_iniciales.json').read_text(encoding='utf-8'))
    tables = ', '.join(f'"juego_{name}"' for name in TABLES)
    lines = [
        '-- PostgreSQL: datos de ejemplo de mi_proyecto_routing.',
        '-- Generado desde juego/fixtures/datos_iniciales.json con generar_seed.py.',
        '-- Ejecutar después de manage.py migrate o de schema.sql, en una BD nueva.',
        '-- Si ya existe cualquier dato del juego, se omite toda la carga.',
        '-- No crea cuentas de autenticación JWT ni administradores.',
        'BEGIN;',
        "SET LOCAL client_encoding = 'UTF8';",
        'SET LOCAL standard_conforming_strings = on;',
        'SET LOCAL search_path = public;',
        'DO $routing_seed$',
        'BEGIN',
        f'    LOCK TABLE {tables} IN SHARE ROW EXCLUSIVE MODE;',
        '    IF ' + '\n       OR '.join(f'EXISTS (SELECT 1 FROM "juego_{name}")' for name in TABLES) + ' THEN',
        "        RAISE NOTICE 'Seed omitido: ya existen datos del juego; no se modifica ningún registro.';",
        '        RETURN;',
        '    END IF;',
    ]
    for name, fields in TABLES.items():
        columns = ['id', *fields]
        rows = []
        for item in fixture:
            if item['model'] != f'juego.{name}':
                continue
            values = [item['pk']]
            for field in fields:
                key = field[:-3] if field.endswith('_id') else field
                values.append(item['fields'].get(key, '' if field == 'tipo' else None))
            rows.append('        (' + ', '.join(literal(v) for v in values) + ')')
        column_sql = ', '.join(f'"{column}"' for column in columns)
        lines += ['', f'    INSERT INTO "juego_{name}" ({column_sql}) VALUES', ',\n'.join(rows) + ';']
    lines += ['', '    -- Ajustar identidades después de insertar IDs explícitos.']
    for name in TABLES:
        table = f'juego_{name}'
        lines.append(f"    PERFORM setval(pg_get_serial_sequence('{table}', 'id'), (SELECT MAX(id) FROM \"{table}\"), true);")
    lines += ["    RAISE NOTICE 'Seed cargado: 2 usuarios, 2 perfiles, 7 habilidades, 7 personajes y 13 relaciones.';",
              'END;', '$routing_seed$;', 'COMMIT;', '']
    (folder / 'seed.sql').write_text('\n'.join(lines), encoding='utf-8')
    print('Generado sql/seed.sql a partir del fixture.')


if __name__ == '__main__':
    main()
