-- PostgreSQL: datos de ejemplo de mi_proyecto_routing.
-- Generado desde juego/fixtures/datos_iniciales.json con generar_seed.py.
-- Ejecutar después de manage.py migrate o de schema.sql, en una BD nueva.
-- Si ya existe cualquier dato del juego, se omite toda la carga.
-- No crea cuentas de autenticación JWT ni administradores.
BEGIN;
SET LOCAL client_encoding = 'UTF8';
SET LOCAL standard_conforming_strings = on;
SET LOCAL search_path = public;
DO $routing_seed$
BEGIN
    LOCK TABLE "juego_usuario", "juego_perfil", "juego_habilidad", "juego_personaje", "juego_personajehabilidad" IN SHARE ROW EXCLUSIVE MODE;
    IF EXISTS (SELECT 1 FROM "juego_usuario")
       OR EXISTS (SELECT 1 FROM "juego_perfil")
       OR EXISTS (SELECT 1 FROM "juego_habilidad")
       OR EXISTS (SELECT 1 FROM "juego_personaje")
       OR EXISTS (SELECT 1 FROM "juego_personajehabilidad") THEN
        RAISE NOTICE 'Seed omitido: ya existen datos del juego; no se modifica ningún registro.';
        RETURN;
    END IF;

    INSERT INTO "juego_usuario" ("id", "nombre", "contrasena", "correo") VALUES
        (1, 'aventurero', 'pbkdf2_sha256$1500000$BxTDQ9auxK62kdZRpn38ji$bXlWFa6ERwz1Z30w8nxTMY5g5fX5iqfBxrpUBaZqNJc=', 'aventurero@example.com'),
        (2, 'exploradora', 'pbkdf2_sha256$1500000$K7Q3wLHDltkBRC8po88cCt$RdxBMfgMku5EB3pQRQqsYUIpVdsG8cpulZov8YDAvEw=', 'exploradora@example.com');

    INSERT INTO "juego_perfil" ("id", "usuario_id", "biografia", "avatar") VALUES
        (1, 1, 'Perfil de aventurero en el mundo del juego.', 'https://example.com/avatar-1.png'),
        (2, 2, 'Perfil de exploradora en el mundo del juego.', 'https://example.com/avatar-2.png');

    INSERT INTO "juego_habilidad" ("id", "nombre", "tipo", "descripcion", "incremento_ataque", "incremento_defensa", "incremento_estamina") VALUES
        (1, 'Espadazo', '', 'Un ataque poderoso con la espada.', 10, 0, -5),
        (2, 'Escudo de Hierro', '', 'Aumenta la defensa del guerrero.', 0, 15, -3),
        (3, 'Bola de Fuego', '', 'Lanza una bola de fuego que causa gran daño.', 20, 0, -10),
        (4, 'Curacion Magica', '', 'Recupera energia y fortalece la resistencia.', 0, 10, 15),
        (5, 'Flecha Veloz', '', 'Dispara una flecha rapida y precisa.', 15, 0, -5),
        (6, 'Ataque Furtivo', '', 'Realiza un ataque sorpresa contra el enemigo.', 25, -5, -10),
        (7, 'Piel de Piedra', '', 'Endurece la piel para resistir ataques enemigos.', 0, 25, -8);

    INSERT INTO "juego_personaje" ("id", "perfil_id", "nombre", "tipo", "descripcion", "ataque", "defensa", "estamina") VALUES
        (1, 1, 'Gagh-Ar', 'guerrero', 'Un valiente luchador con gran fuerza física.', 80, 70, 60),
        (2, 1, 'Elyra', 'maga', 'Hechicera con gran dominio de la energía mágica.', 65, 40, 90),
        (3, 1, 'Thalion', 'elfo', 'Arquero experto con gran precision y agilidad.', 75, 50, 85),
        (4, 1, 'Zarek', 'asesino', 'Guerrero sigiloso especializado en ataques rapidos.', 90, 35, 80),
        (5, 2, 'Brondar', 'enano', 'Resistente luchador que domina el combate cuerpo a cuerpo.', 70, 95, 55),
        (6, 2, 'Lyanna', 'arquera', 'Experta en ataques a distancia y movimientos veloces.', 85, 45, 90),
        (7, 2, 'Drogath', 'orco', 'Poderoso combatiente conocido por su fuerza y resistencia.', 95, 80, 65);

    INSERT INTO "juego_personajehabilidad" ("id", "personaje_id", "habilidad_id", "nivel") VALUES
        (1, 1, 1, 1),
        (2, 1, 2, 1),
        (3, 2, 2, 1),
        (4, 3, 5, 1),
        (5, 3, 4, 1),
        (6, 4, 6, 1),
        (7, 4, 5, 1),
        (8, 5, 2, 1),
        (9, 5, 7, 1),
        (10, 6, 5, 1),
        (11, 6, 6, 1),
        (12, 7, 1, 1),
        (13, 7, 7, 1);

    -- Ajustar identidades después de insertar IDs explícitos.
    PERFORM setval(pg_get_serial_sequence('juego_usuario', 'id'), (SELECT MAX(id) FROM "juego_usuario"), true);
    PERFORM setval(pg_get_serial_sequence('juego_perfil', 'id'), (SELECT MAX(id) FROM "juego_perfil"), true);
    PERFORM setval(pg_get_serial_sequence('juego_habilidad', 'id'), (SELECT MAX(id) FROM "juego_habilidad"), true);
    PERFORM setval(pg_get_serial_sequence('juego_personaje', 'id'), (SELECT MAX(id) FROM "juego_personaje"), true);
    PERFORM setval(pg_get_serial_sequence('juego_personajehabilidad', 'id'), (SELECT MAX(id) FROM "juego_personajehabilidad"), true);
    RAISE NOTICE 'Seed cargado: 2 usuarios, 2 perfiles, 7 habilidades, 7 personajes y 13 relaciones.';
END;
$routing_seed$;
COMMIT;
