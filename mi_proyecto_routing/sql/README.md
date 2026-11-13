# SQL para PostgreSQL — proyecto de routing

| Archivo | Contenido |
| --- | --- |
| `schema.sql` | Tablas, identidades, índices y restricciones del proyecto; incluye tablas de Django, historial de migraciones, tipos de contenido y permisos. Solo para una base vacía. |
| `seed.sql` | 2 usuarios del juego, 2 perfiles, 7 habilidades, 7 personajes y 13 asignaciones de habilidades. |
| `verificar.sql` | Conteos y consultas para comprobar personajes y habilidades. |
| `generar_seed.py` | Regenera el seed desde `juego/fixtures/datos_iniciales.json`, sin conectarse a una base. |

## En Render

El build ya ejecuta `python manage.py migrate`, que crea las tablas. **No ejecutes `schema.sql` sobre esa base**, porque ya tiene el esquema.

El Blueprint tiene `LOAD_DEMO_DATA=True`: carga automáticamente el fixture en una base nueva. En ese caso basta ejecutar `verificar.sql` si quieres revisar los datos. Si ejecutas `seed.sql`, omitirá la carga cuando encuentre cualquier dato del juego.

Para cargar los datos manualmente con SQL, cambia `LOAD_DEMO_DATA` a `False` en `render.yaml` antes del primer despliegue. Una vez aplicadas las migraciones, ejecuta `seed.sql` y después `verificar.sql`.

Para conectarte desde tu computador usa la **External Database URL** de Render. La conexión interna es para el servicio web. El Blueprint deshabilita conexiones externas con `ipAllowList: []`: para conectar pgAdmin o psql desde tu computador, autoriza tu IP pública en el control de acceso de la base y ajusta el Blueprint para conservar esa regla en futuras sincronizaciones.

## Crear una base nueva manualmente en pgAdmin

1. Crea una base vacía y abre su **Query Tool**.
2. Abre `schema.sql` y ejecuta el archivo completo. Corresponde a Django 6.1.1 y a las migraciones del juego hasta `0003_userprofile`; incluye también las migraciones de las aplicaciones internas instaladas.
3. Abre y ejecuta `seed.sql` completo.
4. Ejecuta `verificar.sql`. Los conteos esperados son **2, 2, 7, 7 y 13** según las tablas indicadas.
5. Si conectas Django a esa base, configura `DATABASE_URL` y ejecuta `python manage.py migrate --check`: el historial exportado permite reconocer las migraciones ya aplicadas. Las migraciones futuras se aplican normalmente con `migrate`.

Como alternativa al paso 2, conecta Django a la base nueva y ejecuta `python manage.py migrate`. Después puedes cargar el mismo `seed.sql`. El esquema SQL es una instantánea para la entrega; las migraciones siguen siendo la fuente para evolucionar la aplicación.

## Ejecutar con psql en PowerShell

Configura `DATABASE_URL` de forma privada para la base de destino. Desde la raíz del repositorio, con `psql` disponible en PATH:

```powershell
if (-not $env:DATABASE_URL) { throw 'Configura DATABASE_URL para la base de destino.' }

# Solo si la base está completamente vacía y NO ejecutaste migrate:
psql -d "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f mi_proyecto_routing/sql/schema.sql

# Una vez que las tablas existan:
psql -d "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f mi_proyecto_routing/sql/seed.sql
psql -d "$env:DATABASE_URL" -v ON_ERROR_STOP=1 -f mi_proyecto_routing/sql/verificar.sql
```

Si `psql` no está en PATH, en tu equipo puedes reemplazar `psql` por `& 'C:\Program Files\PostgreSQL\18\bin\psql.exe'`.

No publiques la conexión ni la contraseña. Estos SQL se ejecutan sobre una base existente: no crean el servicio PostgreSQL, el servidor ni su usuario de conexión.

## Comportamiento del seed y cuentas

- Los valores coinciden con el fixture existente, incluidos los hashes de contraseñas de demostración. Se insertan primero los recursos y después sus relaciones.
- Si alguna tabla del juego tiene registros, se omite toda la carga para no sobrescribir ediciones ni mezclar IDs distintos. Se bloquean escrituras concurrentes durante la comprobación y la carga.
- Se ajustan las secuencias después de insertar IDs explícitos, para que el ORM pueda crear registros nuevos sin reutilizar esos IDs.
- No se crean cuentas JWT ni administradores mediante SQL. Los usuarios del juego son distintos de `auth_user`. La cuenta ADMIN sigue creándose con las variables iniciales de Render y `initialize_deployment`, o con los comandos de Django.
- Para regenerar el seed desde la raíz: `.\.venv\Scripts\python.exe mi_proyecto_routing/sql/generar_seed.py`.

## Comprobación realizada

Se usó PostgreSQL 18 local con bases temporales independientes. Se aplicaron las migraciones y se exportó el esquema; después se restauró en otra base vacía. Se ejecutó el seed dos veces, se compararon todos los valores con el fixture y se comprobaron las secuencias. Una edición existente permaneció intacta tras otra ejecución. `migrate --check` reconoció el historial restaurado. No se modificó la base de trabajo del proyecto ni una base de Render.

Referencias: [bloques DO](https://www.postgresql.org/docs/current/sql-do.html), [secuencias y setval](https://www.postgresql.org/docs/current/functions-sequence.html).
