
SELECT 
    d."id_descarga",
    e."nombre" AS estudiante,
    e."grado",
    a."titulo" AS archivo,
    a."url_archivo",
    d."fecha_descarga"
FROM "DESCARGA" d
JOIN "ESTUDIANTE" e ON d."id_estudiante" = e."id"
JOIN "ARCHIVO" a ON d."id_archivo" = a."id_archivo"
WHERE e."nombre" = 'Carter Zenke'
  AND e."grado" IN ('8°', '9°', '10°', '11°');

-- 2. Consultar todas las descargas asociadas a un archivo específico por su título
SELECT 
    d."id_descarga",
    e."nombre" AS estudiante,
    e."grado",
    a."titulo" AS archivo,
    a."url_archivo",
    d."fecha_descarga"
FROM "DESCARGA" d
JOIN "ESTUDIANTE" e ON d."id_estudiante" = e."id"
JOIN "ARCHIVO" a ON d."id_archivo" = a."id_archivo"
WHERE a."titulo" = 'Guia_Ejercicios.pdf';

-- 3. Registrar un nuevo estudiante (con grado en el rango de octavo a once: '8°', '9°', '10°' o '11°')
INSERT INTO "ESTUDIANTE" ("id", "id_usuario", "nombre", "grado")
VALUES (1, 10, 'Carter Zenke', '11°');

INSERT INTO "USUARIO" ("id", "id_estudiante", "id_profesor", "id_admin", "correo", "contrasena", "rol")
VALUES (10, 1, NULL, NULL, 'carter.zenke@correo.com', 'password123', 'Estudiante');

-- 4. Registrar un nuevo Profesor
INSERT INTO "PROFESOR" ("id", "id_usuario", "nombre", "materia")
VALUES (1, 20, 'Profesor Admin', 'Sistemas');

INSERT INTO "USUARIO" ("id", "id_estudiante", "id_profesor", "id_admin", "correo", "contrasena", "rol")
VALUES (20, NULL, 1, NULL, 'profesor.admin@correo.com', 'admin123', 'Profesor');

-- 5. Registrar la subida de un nuevo archivo por parte de un profesor
INSERT INTO "ARCHIVO" ("id_archivo", "id_profesor", "titulo", "descripcion", "url_archivo", "fecha_subida")
VALUES (1, 1, 'Guia_Ejercicios.pdf', 'Tarea sobre gestión de archivos', '/static/uploads/tarea1.pdf', CURRENT_TIMESTAMP);

-- 6. Registrar una nueva descarga de un archivo por parte de un estudiante
INSERT INTO "DESCARGA" ("id_descarga", "id_estudiante", "id_archivo", "fecha_descarga")
VALUES (1, 1, 1, CURRENT_TIMESTAMP);