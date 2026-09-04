-- 1. Representar los administradores del sistema
CREATE TABLE IF NOT EXISTS "ADMIN" (
    "id" SERIAL PRIMARY KEY,
    "id_usuario" INTEGER,
    "correo" VARCHAR(100) NOT NULL,
    "contraseña" VARCHAR(255) NOT NULL,
    "rol" VARCHAR(50) NOT NULL
);

-- 2. Representar los profesores
CREATE TABLE IF NOT EXISTS "PROFESOR" (
    "id" SERIAL PRIMARY KEY,
    "id_usuario" INTEGER,
    "nombre" VARCHAR(100) NOT NULL,
    "materia" VARCHAR(100) NOT NULL
);

-- 3. Representar los estudiantes (grados restringidos de 8° a 11°)
CREATE TABLE IF NOT EXISTS "ESTUDIANTE" (
    "id" SERIAL PRIMARY KEY,
    "id_usuario" INTEGER,
    "nombre" VARCHAR(100) NOT NULL,
    "grado" VARCHAR(10) NOT NULL CHECK ("grado" IN ('8°', '9°', '10°', '11°', '8', '9', '10', '11'))
);

-- 4. Representar la tabla central de usuarios (autenticación y vinculación de perfiles)
CREATE TABLE IF NOT EXISTS "USUARIO" (
    "id" SERIAL PRIMARY KEY,
    "id_estudiante" INTEGER,
    "id_profesor" INTEGER,
    "id_admin" INTEGER,
    "correo" VARCHAR(100) UNIQUE NOT NULL,
    "contrasena" VARCHAR(255) NOT NULL,
    "rol" VARCHAR(50) NOT NULL DEFAULT 'Estudiante',
    CONSTRAINT fk_usuario_estudiante FOREIGN KEY ("id_estudiante") REFERENCES "ESTUDIANTE"("id") ON DELETE SET NULL,
    CONSTRAINT fk_usuario_profesor FOREIGN KEY ("id_profesor") REFERENCES "PROFESOR"("id") ON DELETE SET NULL,
    CONSTRAINT fk_usuario_admin FOREIGN KEY ("id_admin") REFERENCES "ADMIN"("id") ON DELETE SET NULL
);

-- Claves foráneas cíclicas/inversas de los perfiles hacia usuario
ALTER TABLE "ADMIN" ADD CONSTRAINT fk_admin_usuario FOREIGN KEY ("id_usuario") REFERENCES "USUARIO"("id") ON DELETE SET NULL;
ALTER TABLE "PROFESOR" ADD CONSTRAINT fk_profesor_usuario FOREIGN KEY ("id_usuario") REFERENCES "USUARIO"("id") ON DELETE SET NULL;
ALTER TABLE "ESTUDIANTE" ADD CONSTRAINT fk_estudiante_usuario FOREIGN KEY ("id_usuario") REFERENCES "USUARIO"("id") ON DELETE SET NULL;

-- 5. Representar los archivos y recursos subidos por los profesores
CREATE TABLE IF NOT EXISTS "ARCHIVO" (
    "id_archivo" SERIAL PRIMARY KEY,
    "id_profesor" INTEGER NOT NULL,
    "titulo" VARCHAR(150) NOT NULL,
    "descripcion" TEXT,
    "url_archivo" TEXT NOT NULL,
    "fecha_subida" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_archivo_profesor FOREIGN KEY ("id_profesor") REFERENCES "PROFESOR"("id") ON DELETE CASCADE
);

-- 6. Representar el historial de descargas realizadas por los estudiantes
CREATE TABLE IF NOT EXISTS "DESCARGA" (
    "id_descarga" SERIAL PRIMARY KEY,
    "id_estudiante" INTEGER NOT NULL,
    "id_archivo" INTEGER NOT NULL,
    "fecha_descarga" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_descarga_estudiante FOREIGN KEY ("id_estudiante") REFERENCES "ESTUDIANTE"("id") ON DELETE CASCADE,
    CONSTRAINT fk_descarga_archivo FOREIGN KEY ("id_archivo") REFERENCES "ARCHIVO"("id_archivo") ON DELETE CASCADE
);

-- Índices para optimizar las búsquedas más frecuentes
CREATE INDEX IF NOT EXISTS "idx_usuario_correo" ON "USUARIO" ("correo");
CREATE INDEX IF NOT EXISTS "idx_archivo_profesor" ON "ARCHIVO" ("id_profesor");
CREATE INDEX IF NOT EXISTS "idx_archivo_titulo" ON "ARCHIVO" ("titulo");
CREATE INDEX IF NOT EXISTS "idx_descarga_estudiante" ON "DESCARGA" ("id_estudiante");
CREATE INDEX IF NOT EXISTS "idx_descarga_archivo" ON "DESCARGA" ("id_archivo");