-- Buscar todas las entregas dado el número de identificación de un estudiante
SELECT 
    s."id" AS submission_id,
    u."nombre" AS estudiante,
    p."name" AS problema,
    s."submission_path",
    s."correctness",
    s."timestamp"
FROM "submissions" s
JOIN "usuarios" u ON s."student_id" = u."id"
JOIN "problems" p ON s."problem_id" = p."id"
WHERE u."numero_identificacion" = 10111213;

-- Buscar todas las entregas asociadas a un problema específico por su nombre
SELECT 
    s."id" AS submission_id,
    u."nombre" AS estudiante,
    p."name" AS problema,
    s."submission_path",
    s."correctness",
    s."timestamp"
FROM "submissions" s
JOIN "usuarios" u ON s."student_id" = u."id"
JOIN "problems" p ON s."problem_id" = p."id"
WHERE p."name" = 'Packages';

-- Registrar un nuevo estudiante
INSERT INTO "usuarios" ("numero_identificacion", "nombre", "rol", "grupo", "tecnica", "contrasena")
VALUES (10111213, 'Carter Zenke', 'estudiante', '11-1', 'Sistemas', 'password123');

-- Registrar un nuevo instructor
INSERT INTO "usuarios" ("numero_identificacion", "nombre", "rol", "grupo", "tecnica", "contrasena")
VALUES (99887766, 'Profesor Admin', 'profesor', NULL, 'Sistemas', 'admin123');

-- Registrar una nueva entrega (asociando ID del estudiante e ID del problema)
INSERT INTO "submissions" ("student_id", "problem_id", "submission_path", "correctness")
VALUES (1, 1, '/static/uploads/tarea1.pdf', 1.00);

-- Agregar un comentario de un instructor a una entrega
INSERT INTO "comments" ("instructor_id", "submission_id", "contents")
VALUES (2, 1, 'Excelente trabajo, la solución cumple con todos los requisitos.');