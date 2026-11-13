-- Ejecutar después de seed.sql. En una BD nueva deben aparecer: 2, 2, 7, 7, 13.
SELECT 'usuarios' AS tabla, COUNT(*) AS registros FROM public.juego_usuario
UNION ALL SELECT 'perfiles', COUNT(*) FROM public.juego_perfil
UNION ALL SELECT 'habilidades', COUNT(*) FROM public.juego_habilidad
UNION ALL SELECT 'personajes', COUNT(*) FROM public.juego_personaje
UNION ALL SELECT 'personaje_habilidad', COUNT(*) FROM public.juego_personajehabilidad;

-- Personajes y dueño del perfil, sin publicar hashes de contraseñas.
SELECT p.id, p.nombre, p.tipo, u.nombre AS usuario,
       p.ataque, p.defensa, p.estamina
FROM public.juego_personaje AS p
JOIN public.juego_perfil AS perfil ON perfil.id = p.perfil_id
JOIN public.juego_usuario AS u ON u.id = perfil.usuario_id
ORDER BY p.id;

-- Habilidades asignadas y nivel de adquisición.
SELECT p.nombre AS personaje, h.nombre AS habilidad, ph.nivel
FROM public.juego_personajehabilidad AS ph
JOIN public.juego_personaje AS p ON p.id = ph.personaje_id
JOIN public.juego_habilidad AS h ON h.id = ph.habilidad_id
ORDER BY p.id, h.id;
