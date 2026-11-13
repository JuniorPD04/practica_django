# 12 - Despliegue Django en Render - API Juego

## Importar y configurar

1. En Postman selecciona **Import → Files** e importa `actividad_12_despliegue.postman_collection.json`.
2. La colección aparece con el nombre **12 - Despliegue Django en Render - API Juego** y 22 solicitudes numeradas.
3. Importa también el entorno que vayas a utilizar:
   - `actividad_12_render.postman_environment.json`: selecciona **12 - Render - API Juego**. Ya incluye `https://routing-api-kde6.onrender.com` como `base_url`.
   - `actividad_12_local.postman_environment.json`: selecciona **12 - Local - API Juego**. Su URL es `http://127.0.0.1:8000` y presupone `DEBUG=True`.
4. En **Variables** de la colección completa `username` y `password` con la cuenta Django ADMIN creada durante el despliegue. Usa valores locales o privados de Postman; no compartas ni exportes las credenciales reales. Los archivos entregados tienen las credenciales y tokens vacíos.
5. Ejecuta las solicitudes en orden, individualmente con **Send** o con **Run collection**, una iteración y todas seleccionadas.

`base_url` no debe incluir `/api`, rutas adicionales ni barra final. La colección y el entorno Render ya usan la URL publicada; para trabajar localmente selecciona el entorno Local. Las variables del entorno tienen prioridad sobre las de colección.

## Solicitudes incluidas

| Solicitudes | Verificación |
| --- | --- |
| 01–02 | `/authors` público con los tres nombres y códigos; variantes con y sin barra. |
| 03–04 | Perfil y usuarios protegidos sin token: HTTP 401. |
| 05 | Login y captura automática de `access_token` y `refresh_token`. |
| 06–07 | Perfil autenticado con rol ADMIN y lista de usuarios sin contraseñas. |
| 08–12 | Personajes de usuario, catálogo, filtro por tipo, detalle y habilidades asignadas. |
| 13–15 | Catálogo de habilidades, filtro por nombre y detalle. |
| 16–17 | Renovación del access y consulta con el token renovado. |
| 18–19 | Tokens inválidos: HTTP 401. |
| 20 | Personaje inexistente: HTTP 404. |
| 21 | Ataque negativo: HTTP 400 y error asociado al campo. |
| 22 | Logs internos: HTTP 404 en producción, HTTP 200 en desarrollo. |

Los estados 400, 401 y 404 en los casos negativos son resultados esperados: las pruebas deben aparecer en verde. Revisa la pestaña **Test Results** de cada respuesta o el resumen del Runner.

## Variables

| Variable | Uso |
| --- | --- |
| `base_url` | URL base del servidor; el entorno seleccionado la proporciona. |
| `username`, `password` | Credenciales de la cuenta de autenticación Django con perfil ADMIN. |
| `access_token`, `refresh_token` | El login los guarda en variables de colección; el refresh actualiza el access. |
| `usuario_id` | Usuario del juego para consultar sus personajes; inicialmente `1`. |
| `personaje_id` | Personaje existente para consultas; inicialmente `1`. |
| `habilidad_id` | Habilidad existente para consultas; inicialmente `1`. |
| `expect_debug` | `false` para Render; `true` para el servidor local con DEBUG activado. |

No crees variables de entorno llamadas `access_token` o `refresh_token`: ocultarían los valores que el login guarda en la colección. El login limpia los tokens anteriores antes de solicitar otros. La colección utiliza autenticación Bearer heredada; las rutas públicas y los casos sin token la desactivan expresamente.

## Requisitos y alcance

- El backend debe tener sus migraciones y el seed cargados. Los IDs de consulta presuponen los registros de ejemplo; si cambiaste esos registros, configura los IDs correspondientes.
- El login usa la cuenta de `auth_user`, no los usuarios de `juego_usuario`. Ser superusuario de Django no asigna automáticamente el perfil ADMIN; `initialize_deployment` sí crea ambos para la cuenta inicial.
- Si se obtiene 403 al consultar usuarios, revisa `UserProfile.role`. Si el login devuelve 401, comprueba las credenciales y que estés consultando el servidor correcto.
- No se crean, actualizan ni eliminan datos del juego durante la ejecución: el POST de validación es inválido y debe rechazarse. El middleware existente registra las solicitudes en su tabla de logs.
- El middleware actual elimina también el campo `id` del JSON. Estas pruebas no dependen de capturarlo ni modifican ese comportamiento del backend.
- El primer acceso a Render Free puede tardar mientras se reactiva el servicio. Abre `/authors` y espera a que responda antes de ejecutar el Runner.
- Los archivos son exportaciones JSON Postman v2.1 listas para importar; no requieren instalar el CLI, iniciar sesión en un workspace ni publicar documentación.

## Verificación realizada

Se ejecutó la colección mediante Newman contra el backend Django real con una base SQLite temporal y una cuenta ADMIN de prueba. En desarrollo se completaron **22 solicitudes y 41 comprobaciones sin fallos**. Se repitió con DEBUG=False y el encabezado HTTPS del proxy simulado: **22 solicitudes y 41 comprobaciones sin fallos**. Se verificaron los scripts de login, captura de tokens y renovación. No se usaron credenciales reales ni se modificó la base de trabajo. La ejecución contra la URL pública de Render queda a cargo del usuario después de configurar su entorno.

El 13/11/2026 se comprobó además que `https://routing-api-kde6.onrender.com/authors` devuelve HTTP 200 con los tres integrantes y códigos correctos. Esto verifica ese endpoint público; el flujo JWT completo en Render requiere las credenciales privadas del usuario.
