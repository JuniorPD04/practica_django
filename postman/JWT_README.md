# Colección JWT manual

Importa `jwt_autenticacion.postman_collection.json` en Postman. Las 15 solicitudes aparecen directamente en la colección, sin carpetas, scripts ni pruebas automáticas.

Inicia Django con el entorno virtual activo:

```powershell
cd mi_proyecto_routing
python manage.py runserver
```

## Variables necesarias

| Variable | Valor o uso |
| --- | --- |
| `base_url` | `http://127.0.0.1:8000/api`, sin barra final |
| `admin_username` | `admin` |
| `admin_password` | `admin` |
| `access_token` | Copia aquí el access del login de admin |
| `refresh_token` | Copia aquí el refresh del login de admin |
| `user_username` | Usuario Django con rol USER |
| `user_password` | Contraseña de ese usuario |
| `user_access_token` | Copia aquí el access del login USER |

Edita los valores en la pestaña **Variables** de la colección. Evita variables de entorno con los mismos nombres, ya que tienen prioridad.

## Cómo probar

1. Envía **01 - Login admin**. Debe responder 200 con `access` y `refresh`. El login usa username y password; no requiere correo.
2. Copia los tokens a `access_token` y `refresh_token` manualmente.
3. Envía **03 - Mi perfil con token**. Debe responder 200 con los datos de admin.
4. Las solicitudes 02, 04 y 05 deben responder 401: contraseña incorrecta, sin token y token inválido.
5. Envía **06 - Renovar access**. Debe responder 200. Copia el nuevo `access` a `access_token` y prueba la solicitud 07, que debe responder 200.
6. Las solicitudes 08 y 09 deben responder 401: refresh inválido y refresh usado como access.

Las solicitudes ya incluyen la configuración Bearer o No Auth correspondiente. Los tokens no se guardan automáticamente: envía las solicitudes manualmente y revisa sus respuestas.

## Pruebas de roles (solicitudes 10 a 15)

La ruta de tu proyecto es `/api/usuarios/`, protegida con `IsAuthenticated` e `IsAdmin`. Devuelve usuarios del juego (`id`, `nombre`, `correo`), no cuentas de autenticación de Django.

Asigna un `UserProfile` con rol ADMIN al usuario Django admin y prepara otro usuario Django con perfil USER. Ser superusuario no asigna automáticamente el rol ADMIN del perfil.

Completa `user_username` y `user_password`, envía la solicitud 10 y copia su `access` a `user_access_token`. Las solicitudes 11 y 13 deben mostrar los roles USER y ADMIN. Al consultar `/api/usuarios/`, se espera 403 para USER, 200 para ADMIN y 401 sin token.

**Detalle pendiente en el backend:** en el archivo `juego/permissions.py` revisado, `has_permission` está fuera de la clase `IsAdmin`. Debe estar indentado dentro de ella para que DRF compruebe el rol; de lo contrario, un USER puede pasar ese permiso y la solicitud 12 no devolverá el 403 esperado.

## Validación

Se validaron el JSON y sus cuerpos, y se comprobó que no contiene scripts ni eventos. No se ejecutaron solicitudes contra el servidor.
