# Despliegue del proyecto de routing

Este repositorio contiene dos proyectos Django. El Blueprint `render.yaml`, ubicado en la raíz del repositorio, despliega **mi_proyecto_routing**. Su `rootDir` es `mi_proyecto_routing`, y su módulo WSGI es `mi_proyecto_routing.wsgi:application`.

Servicio publicado: https://routing-api-kde6.onrender.com. Se verificó `/authors` con HTTP 200 y los tres integrantes correctos el 13/11/2026.

## 1. Subir los cambios a GitHub

Desde la raíz del repositorio, en PowerShell:

```powershell
git status
# Estos archivos ya estaban versionados. .gitignore no los quita del índice.
# --cached conserva intactas las bases locales en tu computador.
git rm --cached --ignore-unmatch mi_proyecto/db.sqlite3 mi_proyecto_routing/db.sqlite3
git add .gitignore .gitattributes requirements.txt render.yaml mi_proyecto_routing
git diff --cached --stat
git commit -m "Preparar API routing para Render y PostgreSQL"
git push origin main
```

Repositorio existente: https://github.com/JuniorPD04/practica_django. Comprueba en GitHub que sea público, como exige la entrega. No crees otro repositorio ni vuelvas a ejecutar `git init`. Revisa los cambios antes del commit. Nunca agregues `.env` con `-f`.

Quitar SQLite del índice evita publicarlo en próximos commits; no borra las versiones que ya estaban en el historial. Si en algún momento publicaste credenciales reales, debes rotarlas. La SECRET_KEY de producción será nueva y la genera Render.

## 2. Crear el Blueprint en Render

1. Entra a https://dashboard.render.com y accede con tu cuenta de GitHub.
2. Autoriza acceso al repositorio `JuniorPD04/practica_django`.
3. Selecciona **New → Blueprint** y el repositorio. Elige la rama `main` y el archivo `render.yaml` de la raíz.
4. Revisa que se creen `routing-api` y `routing-db`, ambos con plan **Free** y región **Oregon**. Si esos nombres ya existen, cámbialos en el YAML y actualiza también la referencia `fromDatabase.name`.
5. Completa las variables solicitadas con tus propios valores:

| Variable | Qué introducir |
| --- | --- |
| `DJANGO_SUPERUSER_USERNAME` | Nombre para la cuenta de administración y login JWT |
| `DJANGO_SUPERUSER_EMAIL` | Tu correo |
| `DJANGO_SUPERUSER_PASSWORD` | Contraseña larga, única, que guardarás de forma privada |

6. Pulsa **Deploy / Apply** y espera a que ambos recursos estén disponibles. Usa la URL real del Web Service, que puede tener un sufijo asignado por Render.

El Blueprint configura automáticamente `DATABASE_URL` con la conexión interna de PostgreSQL, genera `SECRET_KEY`, establece `DEBUG=False` y permite el hostname exacto de Render. No necesitas copiar una URL de base de datos ni crear un `.env` en Render.

La carpeta [`sql/`](sql/README.md) incluye el esquema PostgreSQL, `seed.sql` y consultas de verificación. En Render el build ya crea las tablas con migraciones; no ejecutes allí el esquema manual sobre las tablas existentes. La guía SQL explica la carga manual como alternativa.

El build instala dependencias, recoge estáticos, aplica migraciones y ejecuta `initialize_deployment`. Este comando crea la cuenta inicial con `UserProfile.role=ADMIN` y carga `datos_iniciales` únicamente cuando todas las tablas del juego están vacías. Los redespliegues conservan datos y contraseñas. El fixture contiene usuarios del juego; las cuentas JWT pertenecen al modelo de autenticación de Django y son independientes.

Después del primer despliegue correcto, elimina **juntas** `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` y `DJANGO_SUPERUSER_PASSWORD` de Environment. La cuenta ya persistirá en PostgreSQL. Si mantienes las variables, el comando no cambia una cuenta existente. No hay una contraseña predeterminada en el código.

## 3. Verificar la entrega

Abre `https://routing-api-kde6.onrender.com/authors` sin token. Debe devolver:

```json
[
  {"nombre": "Junior Perez Davila", "codigo": "407721"},
  {"nombre": "Claudia Libertad Quispe Terrones", "codigo": "407719"},
  {"nombre": "Samuel Andres Zona Malaver", "codigo": "385387"}
]
```

En Postman, usa tu URL real como base:

1. `GET /authors`: 200, sin autenticación.
2. `POST /api/login/`: Body → raw → JSON, `{"username":"TU_USUARIO","password":"TU_CONTRASEÑA"}`. Debe devolver `access` y `refresh`.
3. `GET /api/me/`: Authorization → Bearer Token → pega `access`. Debe indicar el usuario y rol `ADMIN`.
4. `GET /api/usuarios/`: con el mismo token, debe devolver los usuarios de ejemplo.
5. `GET /api/personajes`: debe devolver el catálogo cargado.
6. `GET /admin/`: comprueba que carguen los estilos y que puedas ingresar con la cuenta creada.

El frontend existente en `/` también usa el backend publicado, pero su despliegue no es parte de la entrega. Algunas rutas antiguas del juego usan vistas Django públicas; `DEFAULT_PERMISSION_CLASSES` solo protege vistas DRF. No supongas que toda la API exige JWT: prueba permisos por ruta. `/api/request-logs` devuelve 404 en producción para no publicar registros internos.

## 4. PDF para Teams

En `entrega/` están las 15 respuestas y el PDF con portada, integrantes y la URL pública actualizada. Incluye la captura original `imagen_autores.png` como evidencia. El cuestionario usa una sola columna, tipografía Times, texto negro, párrafos justificados, interlineado 1.5 y guiones cortos, con una presentación académica adaptada a lo solicitado. Para volver a generarlo, conserva la imagen junto al generador:

```powershell
# Desde la raíz del repositorio; la librería del PDF no es dependencia del servidor.
.\.venv\Scripts\python.exe -m pip install -r mi_proyecto_routing/entrega/requirements.txt
.\.venv\Scripts\python.exe mi_proyecto_routing/entrega/generar_pdf.py --url https://routing-api-kde6.onrender.com
```

Entrega en Teams `mi_proyecto_routing/entrega/Perez_Junior_Despliegue.pdf`, la URL pública y el enlace al repositorio. Las capturas son opcionales. El endpoint público de autores ya fue verificado; completa también las pruebas autenticadas con tu cuenta ADMIN.

## 5. Desarrollo y comprobaciones locales

Ya se preparó un `.env` local ignorado por Git con una clave aleatoria. En otra máquina, copia `.env.example` a `.env` dentro de `mi_proyecto_routing` y reemplaza la clave con el resultado de `python -c "import secrets; print(secrets.token_urlsafe(50))"`. Deja `DATABASE_URL` vacío para SQLite y `DEBUG=True`.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DEBUG = 'True'
.\.venv\Scripts\python.exe mi_proyecto_routing/manage.py migrate
.\.venv\Scripts\python.exe mi_proyecto_routing/manage.py runserver
```

Las variables del sistema tienen prioridad sobre `.env`; el ejemplo fija DEBUG explícitamente en PowerShell para evitar conflictos con una variable heredada. Gunicorn se ejecuta en Linux (Render); en Windows usa `runserver`.

```powershell
$env:DEBUG = 'True'
.\.venv\Scripts\python.exe mi_proyecto_routing/manage.py test juego.test_deployment --noinput
.\.venv\Scripts\python.exe mi_proyecto_routing/manage.py collectstatic --no-input
$env:DEBUG = 'False'
.\.venv\Scripts\python.exe mi_proyecto_routing/manage.py check --deploy
```

Las pruebas nuevas verifican `/authors`, HTTPS detrás del proxy, hosts permitidos e inicialización sin sobrescrituras. La suite histórica contiene expectativas de actividades anteriores incompatibles con cambios posteriores (autenticación, eliminación de `id` y validaciones); consulta `entrega/VERIFICACION.md` para el resultado y alcance de la comprobación.

## 6. Si necesitas configurar los servicios manualmente

Crea primero PostgreSQL Free y después un Web Service Python Free, ambos en Oregon. En el Web Service configura:

| Campo | Valor |
| --- | --- |
| Root Directory | `mi_proyecto_routing` |
| Build Command | `bash build.sh` |
| Start Command | `gunicorn mi_proyecto_routing.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile -` |
| Health Check Path | `/authors` |
| `PYTHON_VERSION` | `3.13.5` |
| `DATABASE_URL` | Internal Database URL del PostgreSQL |
| `SECRET_KEY` | Cadena aleatoria de al menos 50 caracteres |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` (el hostname de Render se agrega automáticamente) |
| `LOAD_DEMO_DATA` | `True` |

Añade también las tres variables de la cuenta inicial. No uses `preDeployCommand` ni Shell: no están disponibles en el plan gratuito. No ejecutes los comandos desde la carpeta `mi_proyecto`.

## 7. Límites y errores frecuentes

- El Web Service Free duerme después de 15 minutos sin tráfico; reactivarse puede tomar aproximadamente un minuto. Abre `/authors` con anticipación a la exposición.
- PostgreSQL Free expira a los 30 días. Después hay un período de gracia de 14 días para pasar a pago antes de eliminarse. Planifica exportar datos antes de la expiración; el plan gratuito no incluye backups administrados.
- El disco del Web Service es efímero: SQLite no sirve para persistir producción. Si falta `DATABASE_URL` en Render, el proyecto falla explícitamente en lugar de escribir en SQLite.
- `DisallowedHost`: comprueba el hostname. Si añades dominio propio, agrégalo a `ALLOWED_HOSTS` separado por coma. Para admin bajo dominio propio, configura también sus orígenes CSRF según Django.
- Error de conexión: comprueba que ambos recursos compartan región y que la BD siga activa.
- Error de build por credenciales parciales: introduce usuario y contraseña juntos o elimina ambos.
- Login 401: usa la cuenta Django creada en el despliegue, no los usuarios del fixture. Un 403 en usuarios indica que falta el rol ADMIN.

Fuentes oficiales: [Django en Render](https://render.com/docs/deploy-django), [Blueprint](https://render.com/docs/blueprint-spec), [límites Free](https://render.com/docs/free). Para mantener PostgreSQL más tiempo, puedes evaluar [Neon](https://neon.com/pricing) o [Supabase](https://supabase.com/pricing), con sus límites propios. Si cambias de proveedor, actualiza también `DATABASE_URL` en el Blueprint para que una sincronización no restaure la referencia anterior.
