# Verificaci?n del despliegue

- `check --deploy` con DEBUG=False: sin errores ni advertencias de Django.
- `collectstatic --no-input`: 159 archivos recogidos y 459 procesados.
- `pip check`: sin incompatibilidades declaradas entre dependencias instaladas.
- Tres pruebas nuevas de despliegue: correctas. Cubren autores p?blicos sin JWT, HTTPS y hosts, creaci?n de la cuenta ADMIN, login JWT, acceso autenticado e inicializaci?n repetida sin sobrescribir datos o contrase?as.
- Suite completa actual: 37 pruebas; 7 fallos y 8 errores heredados.
- Comprobaci?n de referencia: se extrajo HEAD con git archive en una carpeta temporal ignorada y se ejecut? la suite original sin los cambios de despliegue. Resultado: 34 pruebas; los mismos 7 fallos y 8 errores, en los mismos casos.

Los fallos previos incluyen sanitizaci?n que elimina tambi?n `id`, pruebas anteriores que consultan usuarios sin JWT y validaci?n que acepta un nombre vac?o. Se conserva el comportamiento previo de las actividades; el despliegue no corrige esos problemas. No debe interpretarse la preparaci?n para Render como una certificaci?n de seguridad de todas las rutas existentes.

No se ejecutó Gunicorn en Windows ni se accedió a la base de Render. Inicialmente las migraciones y el flujo JWT se probaron con SQLite temporal. Posteriormente se verificaron las migraciones y los archivos de la carpeta sql sobre PostgreSQL 18 local aislado: restauración del esquema, 31 registros iguales al fixture, ejecuciones repetidas, secuencias y conservación de ediciones. Django reconoció el historial restaurado mediante migrate --check. No se modificó la base de trabajo del usuario. El 13/11/2026 se verificó además que https://routing-api-kde6.onrender.com/authors devuelve HTTP 200 con los tres integrantes y códigos correctos. Esto no sustituye las pruebas autenticadas ni una comprobación directa del motor de base de datos en Render.

El PDF ya incluye la portada, las 15 respuestas y la URL publicada. La colección 12 y el entorno Render también incluyen esa URL; las credenciales y tokens permanecen vacíos. No se hizo commit ni push de estas actualizaciones.
