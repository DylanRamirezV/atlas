# Documento de Diseño: Base de Datos de Gestión de Usuarios y Descargas Académicas

---

## 🎯 Alcance

La base de datos está diseñada para gestionar la administración de usuarios (administradores, profesores y estudiantes), la carga de recursos/archivos por parte de los profesores y administradores, y el seguimiento de las descargas realizadas por estudiantes y profesores.

El alcance de la base de datos incluye:

* **Administradores (`ADMIN`):** Gestión de credenciales, roles, creación de cuentas de usuario y subida directa de archivos.
* **Usuarios (`USUARIO`):** Entidad central para autenticación y control de acceso (asociada a administradores, profesores y estudiantes).
* **Profesores (`PROFESOR`):** Información sobre el cuerpo docente y las materias que imparten.
* **Estudiantes (`ESTUDIANTE`):** Información de identificación del alumno y su grado académico.
* **Archivos (`ARCHIVO`):** Registro de los materiales y documentos subidos tanto por profesores como por administradores.
* **Descargas (`DESCARGA`):** Registro de las descargas realizadas por los estudiantes y profesores sobre los archivos disponibles.

> 🚫 **Fuera del alcance:** Evaluaciones, calificaciones, entregas de tareas por parte de alumnos, foros de discusión o pagos de colegiatura.

---

## ⚙️ Requisitos Funcionales

Esta base de datos soportará:

* Operaciones **CRUD** para usuarios, administradores, profesores, estudiantes y archivos.
* Autenticación centralizada mediante la tabla `USUARIO`.
* Carga de archivos por parte de los profesores y de los administradores asociando título, descripción, URL y fecha.
* Registro de auditoría o historial cada vez que un estudiante o un profesor realiza una descarga sobre un archivo (`DESCARGA`), guardando la fecha y hora exacta.

---

## 📊 Representación

Las entidades se capturan en tablas de **SQL** (compatibles con SQLite / PostgreSQL / MySQL) con el siguiente esquema extraído directamente del diagrama ER:

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

### Relaciones Exactas del Diagrama

A partir de la notación de pata de gallo (Crow's Foot) del diagrama ER proporcionado:

* **ADMIN ↔ USUARIO:**
  * **Crea:** Un `ADMIN` crea de `0` a muchos (`1:N`) registros en `USUARIO`.
  * **Tiene:** Un `ADMIN` se vincula con exactamente un (`1:1`) registro de `USUARIO`.
* **USUARIO ↔ PROFESOR:**
  * **Tiene:** Un `USUARIO` tiene exactamente un (`1:1`) perfil de `PROFESOR`.
* **USUARIO ↔ ESTUDIANTE:**
  * **Tiene:** Un `USUARIO` tiene exactamente un (`1:1`) perfil de `ESTUDIANTE`.
* **ADMIN ↔ ARCHIVO:**
  * **Sube:** Un `ADMIN` puede subir de `1` a muchos (`1:N`) archivos en `ARCHIVO`.
* **PROFESOR ↔ ARCHIVO:**
  * **Sube:** Un `PROFESOR` puede subir de `1` a muchos (`1:N`) archivos en `ARCHIVO`.
* **PROFESOR ↔ DESCARGA:**
  * **Realiza:** Un `PROFESOR` puede realizar de `1` a muchas (`1:N`) descargas registradas en `DESCARGA`.
* **ESTUDIANTE ↔ DESCARGA:**
  * **Realiza:** Un `ESTUDIANTE` realiza de `1` a muchas (`1:N`) descargas registradas en `DESCARGA`.
* **ARCHIVO ↔ DESCARGA:**
  * **Es descargado:** Un `ARCHIVO` puede estar presente en de `1` a muchas (`1:N`) instancias de `DESCARGA`.