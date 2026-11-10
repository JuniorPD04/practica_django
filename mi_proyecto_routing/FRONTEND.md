# Frontend sencillo del taller

- `juego/templates/juego/index.html`: dos inputs, Login, Cargar usuarios y lista.
- `juego/static/juego/js/login.js`: funciones `login()` y `loadUsers()`.
- `juego/static/juego/css/login.css`: estilos básicos.

Desde `mi_proyecto_routing`, con el entorno virtual activo, ejecuta `python manage.py runserver` y abre http://127.0.0.1:8000/.

Login envía las credenciales a `/api/login/` y guarda `data.access` en `sessionStorage` con la clave `token`. La guía usa `data.token`, pero SimpleJWT devuelve `access`.

Cargar usuarios envía ese token como `Authorization: Bearer ...` a `/api/usuarios/`, la ruta existente en este proyecto. Devuelve usuarios del juego con el campo `nombre`, por eso la lista usa `user.nombre` en lugar de `user.username`. No es una lista de cuentas de autenticación de Django.

Esta ruta requiere rol ADMIN en `UserProfile`; ser superusuario de Django no asigna ese rol automáticamente. Un 403 indica que no tienes el permiso requerido. Si no hay usuarios del juego registrados, la lista lo indica.

En F12, revisa Network para las solicitudes, Application → Session Storage para el token y Console para los errores. El access no se renueva automáticamente: cuando expire, vuelve a iniciar sesión.
