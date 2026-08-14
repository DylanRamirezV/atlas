-- 1. Representar los usuarios de la plataforma (estudiantes e instructores)
CREATE TABLE IF NOT EXISTS "usuarios" (
    "id" SERIAL PRIMARY KEY,
    "numero_identificacion" INTEGER UNIQUE NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "rol" VARCHAR(20) NOT NULL DEFAULT 'estudiante',
    "grupo" VARCHAR(50),
    "tecnica" VARCHAR(100),
    "contrasena" VARCHAR(255) NOT NULL
);

-- 2. Representar los problemas o actividades asignadas
CREATE TABLE IF NOT EXISTS "problems" (
    "id" SERIAL PRIMARY KEY,
    "problem_set" INTEGER NOT NULL,
    "name" VARCHAR(100) NOT NULL
);

-- 3. Representar las entregas realizadas por los estudiantes
CREATE TABLE IF NOT EXISTS "submissions" (
    "id" SERIAL PRIMARY KEY,
    "student_id" INTEGER NOT NULL,
    "problem_id" INTEGER NOT NULL,
    "submission_path" TEXT NOT NULL,
    "correctness" NUMERIC(3, 2) NOT NULL CHECK ("correctness" BETWEEN 0 AND 1),
    "timestamp" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_student FOREIGN KEY ("student_id") REFERENCES "usuarios"("id") ON DELETE CASCADE,
    CONSTRAINT fk_problem FOREIGN KEY ("problem_id") REFERENCES "problems"("id") ON DELETE CASCADE
);

-- 4. Representar los comentarios dejados por instructores a las entregas
CREATE TABLE IF NOT EXISTS "comments" (
    "id" SERIAL PRIMARY KEY,
    "instructor_id" INTEGER NOT NULL,
    "submission_id" INTEGER NOT NULL,
    "contents" TEXT NOT NULL,
    CONSTRAINT fk_instructor FOREIGN KEY ("instructor_id") REFERENCES "usuarios"("id") ON DELETE CASCADE,
    CONSTRAINT fk_submission FOREIGN KEY ("submission_id") REFERENCES "submissions"("id") ON DELETE CASCADE
);

-- Índices para optimizar las búsquedas más frecuentes
CREATE INDEX IF NOT EXISTS "idx_usuarios_identificacion" ON "usuarios" ("numero_identificacion");
CREATE INDEX IF NOT EXISTS "idx_problems_name" ON "problems" ("name");
CREATE INDEX IF NOT EXISTS "idx_submissions_student" ON "submissions" ("student_id");
CREATE INDEX IF NOT EXISTS "idx_submissions_problem" ON "submissions" ("problem_id");