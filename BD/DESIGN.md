# Documento de Diseño: Base de Datos de Gestión de Usuarios y Descargas Académicas

---

##  Alcance

La base de datos está diseñada para gestionar la administración de usuarios, la estructura académica (grados y materias), la vinculación de profesores y estudiantes con sus respectivas asignaturas, la carga de recursos/archivos por parte de los profesores y el seguimiento de las descargas realizadas por los estudiantes.

El alcance de la base de datos incluye las siguientes entidades:

* **Administradores (`ADMIN`):** Gestión de credenciales y creación/administración de usuarios.
* **Usuarios (`USUARIO`):** Entidad central para autenticación y control de acceso (asociada a administradores, profesores y estudiantes).
* **Profesores (`PROFESOR`):** Información sobre el cuerpo docente.
* **Estudiantes (`ESTUDIANTE`):** Información de identificación del alumno y su grado académico asociado.
* **Grados (`GRADOS`):** Catálogo de grados o niveles académicos.
* **Materias (`MATERIAS`):** Catálogo de asignaturas disponibles en la institución.
* **Asignaciones de Profesor (`PROFESOR_MATERIA`):** Relación entre profesores y las materias que imparten (dictan).
* **Asignaciones de Estudiante (`ESTUDIANTE_MATERIA`):** Relación entre estudiantes y las materias que cursan.
* **Archivos (`ARCHIVO`):** Registro de materiales y documentos subidos por los profesores, asociados a una materia específica.
* **Descargas (`DESCARGA`):** Registro de las descargas realizadas por los estudiantes sobre los archivos disponibles.

---

##  Requisitos Funcionales

Esta base de datos soportará:

* Operaciones **CRUD** para usuarios, administradores, profesores, estudiantes, grados, materias y archivos.
* Autenticación centralizada mediante la tabla `USUARIO`.
* Gestión de la estructura académica asignando materias a profesores y cursos/materias a estudiantes.
* Carga de archivos por parte de los profesores asociándolos a una materia en específico, junto con título, descripción, URL y fecha.
* Registro de auditoría o historial cada vez que un estudiante realiza una descarga sobre un archivo (`DESCARGA`), guardando la fecha y hora exacta.

---

##  Representación

Las entidades se capturan en tablas **SQL** con el siguiente esquema extraído directamente del diagrama ER:

### Entidades

#### 1. Administrador (`ADMIN`)
Almacena la información de los administradores del sistema.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `int` | `PRIMARY KEY` — Identificador único del administrador. |
| `id_usuario` | `int` | `FOREIGN KEY` — Referencia al usuario correspondiente. |
| `correo` | `string` | Correo electrónico del administrador. |
| `contraseña` | `string` | Contraseña de acceso. |
| `rol` | `string` | Rol asignado. |

#### 2. Usuario (`USUARIO`)
Tabla central de autenticación y vinculación de perfiles.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `int` | `PRIMARY KEY` — Identificador único del usuario. |
| `id_estudiante` | `int` | `FOREIGN KEY` — Identificador asociado si es estudiante. |
| `id_profesor` | `int` | `FOREIGN KEY` — Identificador asociado si es profesor. |
| `id_admin` | `int` | `FOREIGN KEY` — Identificador asociado si es administrador. |
| `correo` | `string` | Correo electrónico para inicio de sesión. |
| `contrasena` | `string` | Contraseña encriptada. |
| `rol` | `string` | Rol del usuario. |

#### 3. Profesor (`PROFESOR`)
Información específica del perfil docente.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `int` | `PRIMARY KEY` — Identificador único del profesor. |
| `id_usuario` | `int` | `FOREIGN KEY` — Referencia al usuario correspondiente. |
| `nombre` | `string` | Nombre completo del profesor. |

#### 4. Grados (`GRADOS`)
Catálogo de grados o niveles académicos.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `int` | `PRIMARY KEY` — Identificador único del grado. |
| `nombre` | `string` | Nombre del grado académico. |

#### 5. Estudiante (`ESTUDIANTE`)
Información específica del perfil del alumno.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `int` | `PRIMARY KEY` — Identificador único del estudiante. |
| `id_usuario` | `int` | `FOREIGN KEY` — Referencia al usuario correspondiente. |
| `id_grado` | `int` | `FOREIGN KEY` — Referencia al grado al que pertenece. |
| `nombre` | `string` | Nombre completo del estudiante. |

#### 6. Materias (`MATERIAS`)
Catálogo de asignaturas o materias educativas.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `int` | `PRIMARY KEY` — Identificador único de la materia. |
| `nombre` | `string` | Nombre de la materia. |

#### 7. Profesor - Materia (`PROFESOR_MATERIA`)
Tabla de unión que asigna las materias impartidas por cada profesor.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `int` | `PRIMARY KEY` — Identificador único del registro. |
| `id_profesor` | `int` | `FOREIGN KEY` — Referencia al profesor. |
| `id_materia` | `int` | `FOREIGN KEY` — Referencia a la materia. |

#### 8. Estudiante - Materia (`ESTUDIANTE_MATERIA`)
Tabla de unión que registra las materias cursadas por cada estudiante.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id` | `int` | `PRIMARY KEY` — Identificador único del registro. |
| `id_estudiante` | `int` | `FOREIGN KEY` — Referencia al estudiante. |
| `id_materia` | `int` | `FOREIGN KEY` — Referencia a la materia. |

#### 9. Archivo (`ARCHIVO`)
Documentos y recursos educativos subidos por los profesores para sus materias.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id_archivo` | `int` | `PRIMARY KEY` — Identificador único del archivo. |
| `id_profesor` | `int` | `FOREIGN KEY` — Profesor que subió el archivo. |
| `id_materia` | `int` | `FOREIGN KEY` — Materia a la que pertenece el archivo. |
| `titulo` | `string` | Título del recurso o documento. |
| `descripcion` | `string` | Descripción del contenido del archivo. |
| `url_archivo` | `string` | Enlace / Ruta de almacenamiento del archivo. |
| `fecha_subida` | `datetime` | Fecha y hora en la que se subió el archivo. |

#### 10. Descarga (`DESCARGA`)
Tabla asociativa/historial que registra las descargas efectuadas por los estudiantes.

| Columna | Tipo de Dato | Restricciones / Descripción |
| :--- | :--- | :--- |
| `id_descarga` | `int` | `PRIMARY KEY` — Identificador único del evento de descarga. |
| `id_estudiante` | `int` | `FOREIGN KEY` — Estudiante que realiza la descarga. |
| `id_archivo` | `int` | `FOREIGN KEY` — Archivo descargado. |
| `fecha_descarga` | `datetime` | Fecha y hora exacta en que se efectuó la descarga. |

---

### Relaciones Exactas del Diagrama

A partir de la notación de pata de gallo (Crow's Foot) del diagrama ER:

* **ADMIN ↔ USUARIO:**
  * **crea:** Un `ADMIN` crea de `0` a muchos (`0:N`) registros en `USUARIO`.
  * **tiene:** Un `ADMIN` se vincula de forma exacta (`1:1`) con `USUARIO`.
* **USUARIO ↔ PROFESOR:**
  * **tiene:** Un `USUARIO` se vincula (`1:1`) con un perfil de `PROFESOR`.
* **USUARIO ↔ ESTUDIANTE:**
  * **pertenece_a / tiene:** Un `USUARIO` se vincula (`1:1`) con un perfil de `ESTUDIANTE`.
* **GRADOS ↔ ESTUDIANTE:**
  * **pertenece_a:** Un `GRADOS` puede tener de `1` a muchos (`1:N`) registros en `ESTUDIANTE`. Un `ESTUDIANTE` pertenece a exactamente un (`1:1`) `GRADOS`.
* **PROFESOR ↔ PROFESOR_MATERIA:**
  * **dicta:** Un `PROFESOR` se relaciona con `1` a muchas (`1:N`) asignaciones en `PROFESOR_MATERIA`.
* **MATERIAS ↔ PROFESOR_MATERIA:**
  * **es_impartida_en:** Una `MATERIAS` se vincula con `1` a muchas (`1:N`) asignaciones en `PROFESOR_MATERIA`.
* **ESTUDIANTE ↔ ESTUDIANTE_MATERIA:**
  * **cursa:** Un `ESTUDIANTE` se relaciona con `1` a muchas (`1:N`) asignaciones en `ESTUDIANTE_MATERIA`.
* **MATERIAS ↔ ESTUDIANTE_MATERIA:**
  * **pertenece_a:** Una `MATERIAS` se vincula con `1` a muchas (`1:N`) asignaciones en `ESTUDIANTE_MATERIA`.
* **PROFESOR ↔ ARCHIVO:**
  * **sube:** Un `PROFESOR` puede subir de `1` a muchos (`1:N`) recursos en `ARCHIVO`.
* **ESTUDIANTE ↔ DESCARGA:**
  * **realiza:** Un `ESTUDIANTE` realiza de `1` a muchas (`1:N`) descargas registradas en `DESCARGA`.
* **ARCHIVO ↔ DESCARGA:**
  * **es_descargado:** Un `ARCHIVO` puede ser descargado en de `1` a muchas (`1:N`) instancias registradas en `DESCARGA`.