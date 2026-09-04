# Documento de Diseño: Base de Datos de Gestión de Usuarios y Descargas Académicas

---

## 🎯 Alcance

La base de datos está diseñada para gestionar la administración de usuarios (administradores, profesores y estudiantes), la carga de recursos/archivos por parte de los profesores y el seguimiento de las descargas realizadas por los estudiantes.

El alcance de la base de datos incluye:

* **Administradores (`ADMIN`):** Gestión de credenciales, roles y creación de cuentas de usuario.
* **Usuarios (`USUARIO`):** Entidad central para autenticación y control de acceso (asociada a administradores, profesores y estudiantes).
* **Profesores (`PROFESOR`):** Información sobre el cuerpo docente y las materias que imparten.
* **Estudiantes (`ESTUDIANTE`):** Información de identificación del alumno y su grado académico.
* **Archivos (`ARCHIVO`):** Registro de los materiales y documentos subidos por los profesores.
* **Descargas (`DESCARGA`):** Registro de las descargas realizadas por los estudiantes sobre los archivos disponibles.

> 🚫 **Fuera del alcance:** Evaluaciones, calificaciones, entregas de tareas por parte de alumnos, foros de discusión o pagos de colegiatura.

---

## ⚙️ Requisitos Funcionales

Esta base de datos soportará:

* Operaciones **CRUD** para usuarios, administradores, profesores, estudiantes y archivos.
* Autenticación centralizada mediante la tabla `USUARIO`.
* Carga de archivos por parte de los profesores asociando título, descripción, URL y fecha.
* Registro de auditoría o historial cada vez que un estudiante descarga un archivo (`DESCARGA`), guardando la fecha y hora exacta.

---

## 📊 Representación

Las entidades se capturan en tablas de **SQL** (compatibles con SQLite / PostgreSQL / MySQL) con el siguiente esquema extraído del diagrama:

### Entidades

#### 1. Administrador (`ADMIN`)
Almacena la información de los administradores del sistema.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `INT` | `PRIMARY KEY` — Identificador único del administrador. |
| `id_usuario` | `INT` | Identificador de relación con usuario. |
| `correo` | `STRING` | Correo electrónico del administrador. |
| `contraseña` | `STRING` | Contraseña de acceso. |
| `rol` | `STRING` | Rol asignado. |

#### 2. Usuario (`USUARIO`)
Tabla central de autenticación y vinculación de perfiles.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `INT` | `PRIMARY KEY` — Identificador único del usuario. |
| `id_estudiante` | `INT` | Identificador asociado si es estudiante. |
| `id_profesor` | `INT` | Identificador asociado si es profesor. |
| `id_admin` | `INT` | Identificador asociado si es administrador. |
| `correo` | `STRING` | Correo electrónico para inicio de sesión. |
| `contrasena` | `STRING` | Contraseña encriptada. |
| `rol` | `STRING` | Rol del usuario (ej. Admin, Profesor, Estudiante). |

#### 3. Profesor (`PROFESOR`)
Información específica del perfil docente.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `INT` | `PRIMARY KEY` — Identificador único del profesor. |
| `id_usuario` | `INT` | `FOREIGN KEY` — Referencia al usuario correspondiente. |
| `nombre` | `STRING` | Nombre completo del profesor. |
| `materia` | `STRING` | Materia o asignatura que imparte. |

#### 4. Estudiante (`ESTUDIANTE`)
Información específica del perfil del alumno.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `INT` | `PRIMARY KEY` — Identificador único del estudiante. |
| `id_usuario` | `INT` | Referencia al usuario correspondiente. |
| `nombre` | `STRING` | Nombre completo del estudiante. |
| `grado` | `STRING` | Grado, curso o nivel académico del estudiante. |

#### 5. Archivo (`ARCHIVO`)
Documentos y recursos educativos subidos a la plataforma.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id_archivo` | `INT` | `PRIMARY KEY` — Identificador único del archivo. |
| `id_profesor` | `INT` | `FOREIGN KEY` — Profesor que subió el archivo. |
| `titulo` | `STRING` | Título del recurso o documento. |
| `descripcion` | `STRING` | Descripción detallada del contenido del archivo. |
| `url_archivo` | `STRING` | Enlace / Ruta donde está almacenado el archivo. |
| `fecha_subida` | `DATETIME` | Fecha y hora en la que se subió el archivo. |

#### 6. Descarga (`DESCARGA`)
Tabla asociativa/historial que registra las descargas efectuadas.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id_descarga` | `INT` | `PRIMARY KEY` — Identificador único del evento de descarga. |
| `id_estudiante` | `INT` | `FOREIGN KEY` — Estudiante que realiza la descarga. |
| `id_archivo` | `INT` | `FOREIGN KEY` — Archivo descargado. |
| `fecha_descarga` | `DATETIME` | Fecha y hora exacta en que se efectuó la descarga. |

---

### Relaciones

A partir del diagrama Entidad-Relación proporcionado:

* **ADMIN ↔ USUARIO (1:1 / 1:N):** Un `ADMIN` crea / tiene asignado un registro en `USUARIO`.
* **USUARIO ↔ PROFESOR (1:1):** Un `USUARIO` tiene asociado un único registro de `PROFESOR`.
* **USUARIO ↔ ESTUDIANTE (1:1):** Un `USUARIO` tiene asociado un único registro de `ESTUDIANTE`.
* **PROFESOR ↔ ARCHIVO (1:N):** Un `PROFESOR` sube de `0` a muchos `ARCHIVOS`. Cada `ARCHIVO` pertenece a un único `PROFESOR`.
* **ESTUDIANTE ↔ DESCARGA (1:N):** Un `ESTUDIANTE` realiza de `0` a muchas `DESCARGAS`.
* **ARCHIVO ↔ DESCARGA (1:N):** Un `ARCHIVO` es descargado en `0` o muchas `DESCARGAS`.

---