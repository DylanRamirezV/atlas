import hmac
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from auth import (
    cerrar_sesion,
    iniciar_sesion,
    requerir_admin,
    requerir_cualquier_rol,
    requerir_estudiante,
    requerir_profesor,
    requerir_profesor_o_admin,
)
from database import get_db
from modelos import Admin, Archivo, Estudiante, Grado, Materia, MateriaGrado, Profesor, ProfesorMateria, Usuario
from storage import eliminar_archivo_storage, subir_archivo_storage

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/", include_in_schema=False)
async def inicio():
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse(
        request,
        "pages/login.html",
        {
            "titulo_app": "Atlas",
            "descripcion_app": "Agrega aqui una descripcion breve sobre el proposito de la app.",
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def procesar_login(
    request: Request,
    correo: str = Form(...),
    contrasena: str = Form(...),
    db: Session = Depends(get_db),
):
    correo_limpio = correo.strip().lower()

    usuario = db.query(Usuario).filter(Usuario.correo == correo_limpio).first()
    if usuario is None or not contrasena_valida(contrasena, usuario.contrasena):
        return templates.TemplateResponse(
            request,
            "partials/login_feedback.html",
            {
                "tipo": "error",
                "titulo": "No pudimos iniciar sesion",
                "mensaje": "Revisa que el correo y la contrasena sean correctos.",
                "correo": correo_limpio,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    iniciar_sesion(request, usuario)
    destino = ruta_por_rol(usuario)

    if request.headers.get("hx-request") == "true":
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers={"HX-Redirect": destino})

    return RedirectResponse(url=destino, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout", include_in_schema=False)
async def logout(request: Request):
    cerrar_sesion(request)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


def contrasena_valida(contrasena_formulario: str, contrasena_guardada: str) -> bool:
    return hmac.compare_digest(contrasena_formulario, contrasena_guardada)


def ruta_por_rol(usuario: Usuario) -> str:
    rol = (usuario.rol or "").strip().lower()

    if rol == "profesor":
        return "/profesor"
    if rol == "admin":
        return "/admin"
    if rol == "estudiante":
        return "/estudiante"

    return "/login"


def obtener_archivos_institucionales(db: Session) -> list[Archivo]:
    return (
        db.query(Archivo)
        .filter(Archivo.id_materia.is_(None), Archivo.id_grado.is_(None))
        .order_by(Archivo.fecha_subida.desc())
        .all()
    )


def obtener_todos_los_grados(db: Session) -> list[Grado]:
    return db.query(Grado).order_by(Grado.grupo.asc()).all()


def obtener_contexto_profesor(db: Session, profesor_id: int) -> dict:
    profesor = db.query(Profesor).filter(Profesor.id == profesor_id).first()

    if profesor is None:
        return {
            "nombre_profesor": "profesor",
            "materias": [],
            "materia_activa": None,
            "grados": [],
            "profesor_id": profesor_id,
            "grado_activo_id": None,
            "archivos_institucionales": obtener_archivos_institucionales(db),
        }

    materias = obtener_materias_profesor(db, profesor)
    materia_activa = materias[0] if materias else None
    grados = obtener_grados_materia(db, materia_activa.id) if materia_activa else []
    grado_activo_id = grados[0].id if grados else None

    return {
        "nombre_profesor": profesor.nombre,
        "materias": materias,
        "materia_activa": materia_activa,
        "grados": grados,
        "profesor_id": profesor.id,
        "grado_activo_id": grado_activo_id,
        "archivos": obtener_archivos_materia_grado(db, materia_activa.id if materia_activa else None, grado_activo_id),
        "archivos_institucionales": obtener_archivos_institucionales(db),
    }


def obtener_materias_profesor(db: Session, profesor: Profesor) -> list[Materia]:
    return (
        db.query(Materia)
        .join(ProfesorMateria, Materia.id == ProfesorMateria.id_materia)
        .filter(ProfesorMateria.id_profesor == profesor.id)
        .order_by(Materia.nombre.asc())
        .all()
    )


def obtener_grados_materia(db: Session, materia_id: int) -> list[Grado]:
    return (
        db.query(Grado)
        .join(MateriaGrado, Grado.id == MateriaGrado.id_grado)
        .filter(MateriaGrado.id_materia == materia_id)
        .order_by(Grado.grupo.asc())
        .all()
    )


def obtener_archivos_materia_grado(db: Session, materia_id: int | None, grado_id: int | None) -> list[Archivo]:
    if not materia_id or not grado_id:
        return []

    return (
        db.query(Archivo)
        .filter(Archivo.id_materia == materia_id, Archivo.id_grado == grado_id)
        .order_by(Archivo.fecha_subida.desc())
        .all()
    )


TIPOS_OFFICE = {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def clasificar_archivo(tipo_mime: str | None, url_archivo: str) -> dict:
    tipo_mime = (tipo_mime or "").lower()
    es_imagen = tipo_mime.startswith("image/")
    es_pdf = tipo_mime == "application/pdf"
    es_office = tipo_mime in TIPOS_OFFICE

    url_visor_office = None
    if es_office:
        url_visor_office = "https://view.officeapps.live.com/op/embed.aspx?src=" + quote(url_archivo, safe="")

    return {
        "es_imagen": es_imagen,
        "es_pdf": es_pdf,
        "es_office": es_office,
        "url_visor_office": url_visor_office,
    }


def obtener_contexto_estudiante(db: Session, estudiante_id: int) -> dict:
    estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()

    if estudiante is None:
        return {
            "nombre_estudiante": "estudiante",
            "estudiante_id": estudiante_id,
            "grado": None,
            "materias": [],
            "materia_activa": None,
            "archivos_materia": [],
            "descargas": [],
            "archivos_institucionales": obtener_archivos_institucionales(db),
        }

    materias = obtener_materias_estudiante(db, estudiante)
    materia_activa = materias[0] if materias else None

    return {
        "nombre_estudiante": estudiante.nombre,
        "estudiante_id": estudiante.id,
        "grado": estudiante.grado,
        "materias": materias,
        "materia_activa": materia_activa,
        "archivos_materia": obtener_archivos_materia_grado(
            db,
            materia_activa.id if materia_activa else None,
            estudiante.id_grado,
        ),
        "descargas": [],
        "archivos_institucionales": obtener_archivos_institucionales(db),
    }


def obtener_materias_estudiante(db: Session, estudiante: Estudiante) -> list[Materia]:
    if estudiante.id_grado is None:
        return []

    return (
        db.query(Materia)
        .join(MateriaGrado, Materia.id == MateriaGrado.id_materia)
        .filter(MateriaGrado.id_grado == estudiante.id_grado)
        .order_by(Materia.nombre.asc())
        .all()
    )


# ---------------------------------------------------------------------------
# PROFESOR (todas las rutas exigen sesion de profesor; el profesor_id nunca
# se toma de la URL, siempre se calcula desde la sesion via requerir_profesor)
# ---------------------------------------------------------------------------

@router.get("/profesor", response_class=HTMLResponse)
async def profesor_inicio(
    request: Request,
    profesor_id: int = Depends(requerir_profesor),
    db: Session = Depends(get_db),
):
    contexto = obtener_contexto_profesor(db, profesor_id)
    return templates.TemplateResponse(
        request,
        "pages/profesor.html",
        {
            **contexto,
            "panel_activo": "institucional",
        },
    )


@router.get("/profesor/panel/{panel}", response_class=HTMLResponse)
async def profesor_panel(
    request: Request,
    panel: str,
    profesor_id: int = Depends(requerir_profesor),
    db: Session = Depends(get_db),
):
    contexto = obtener_contexto_profesor(db, profesor_id)
    plantillas = {
        "institucional": "partials/profesor_institucional.html",
        "materias": "partials/profesor_materias.html",
        "proyecto": "partials/profesor_proyecto.html",
    }

    plantilla = plantillas.get(panel, plantillas["institucional"])
    return templates.TemplateResponse(
        request,
        plantilla,
        {
            **contexto,
            "panel_activo": panel,
        },
    )


@router.get("/profesor/materias/{materia_id}/grados", response_class=HTMLResponse)
async def profesor_grados_materia(
    request: Request,
    materia_id: int,
    profesor_id: int = Depends(requerir_profesor),
    db: Session = Depends(get_db),
):
    materia = (
        db.query(Materia)
        .join(ProfesorMateria, Materia.id == ProfesorMateria.id_materia)
        .filter(Materia.id == materia_id, ProfesorMateria.id_profesor == profesor_id)
        .first()
    )
    grados = obtener_grados_materia(db, materia_id) if materia else []
    grado_activo_id = grados[0].id if grados else None

    return templates.TemplateResponse(
        request,
        "partials/profesor_grados.html",
        {
            "materia_activa": materia,
            "grados": grados,
            "profesor_id": profesor_id,
            "grado_activo_id": grado_activo_id,
            "archivos": obtener_archivos_materia_grado(db, materia_id, grado_activo_id),
        },
    )


@router.get("/profesor/materias/{materia_id}/grados/{grado_id}", response_class=HTMLResponse)
async def profesor_grado_activo(
    request: Request,
    materia_id: int,
    grado_id: int,
    profesor_id: int = Depends(requerir_profesor),
    db: Session = Depends(get_db),
):
    materia = (
        db.query(Materia)
        .join(ProfesorMateria, Materia.id == ProfesorMateria.id_materia)
        .filter(Materia.id == materia_id, ProfesorMateria.id_profesor == profesor_id)
        .first()
    )
    grados = obtener_grados_materia(db, materia_id) if materia else []

    return templates.TemplateResponse(
        request,
        "partials/profesor_grados.html",
        {
            "materia_activa": materia,
            "grados": grados,
            "profesor_id": profesor_id,
            "grado_activo_id": grado_id,
            "archivos": obtener_archivos_materia_grado(db, materia_id, grado_id),
        },
    )


@router.post("/profesor/materias/{materia_id}/grados/{grado_id}/archivos", response_class=HTMLResponse)
async def subir_archivo_materia(
    request: Request,
    materia_id: int,
    grado_id: int,
    nombre: str = Form(...),
    descripcion: str = Form(""),
    archivo: UploadFile = File(...),
    profesor_id: int = Depends(requerir_profesor),
    db: Session = Depends(get_db),
):
    materia = (
        db.query(Materia)
        .join(ProfesorMateria, Materia.id == ProfesorMateria.id_materia)
        .filter(Materia.id == materia_id, ProfesorMateria.id_profesor == profesor_id)
        .first()
    )
    grados = obtener_grados_materia(db, materia_id) if materia else []
    profesor = db.query(Profesor).filter(Profesor.id == profesor_id).first()

    error = None
    if materia is None:
        error = "Esta materia no esta asignada a tu usuario."
    elif profesor is None or profesor.id_usuario is None:
        error = "No se encontro un usuario asociado a este profesor, no se pudo subir el archivo."
    else:
        contenido = await archivo.read()
        carpeta = f"materia_{materia_id}/grado_{grado_id}"
        url_publica = subir_archivo_storage(
            contenido,
            archivo.filename or "archivo",
            carpeta,
            content_type=archivo.content_type,
        )

        nuevo_archivo = Archivo(
            nombre=nombre.strip() or (archivo.filename or "Archivo sin nombre"),
            tipo=archivo.content_type or "application/octet-stream",
            descripcion=descripcion.strip(),
            url_archivo=url_publica,
            id_usuario=profesor.id_usuario,
            id_materia=materia_id,
            id_grado=grado_id,
        )
        db.add(nuevo_archivo)
        db.commit()

    return templates.TemplateResponse(
        request,
        "partials/profesor_grados.html",
        {
            "materia_activa": materia,
            "grados": grados,
            "profesor_id": profesor_id,
            "grado_activo_id": grado_id,
            "archivos": obtener_archivos_materia_grado(db, materia_id, grado_id),
            "error_subida": error,
        },
    )


# ---------------------------------------------------------------------------
# ARCHIVOS (compartidas entre profesor y admin para editar/borrar;
# la previsualizacion la puede usar cualquier rol autenticado)
# ---------------------------------------------------------------------------

@router.get("/archivos/{archivo_id}/editar", response_class=HTMLResponse)
async def obtener_edicion_archivo(
    request: Request,
    archivo_id: int,
    db: Session = Depends(get_db),
    _sesion: dict = Depends(requerir_profesor_o_admin),
):
    archivo = db.query(Archivo).filter(Archivo.id == archivo_id).first()
    return templates.TemplateResponse(
        request,
        "partials/editar_archivo.html",
        {"archivo": archivo},
    )


@router.post("/archivos/{archivo_id}/editar", response_class=HTMLResponse)
async def guardar_edicion_archivo(
    request: Request,
    archivo_id: int,
    nombre: str = Form(...),
    descripcion: str = Form(""),
    db: Session = Depends(get_db),
    _sesion: dict = Depends(requerir_profesor_o_admin),
):
    archivo = db.query(Archivo).filter(Archivo.id == archivo_id).first()
    if archivo is not None:
        archivo.nombre = nombre.strip() or archivo.nombre
        archivo.descripcion = descripcion.strip()
        db.commit()
        db.refresh(archivo)

    return templates.TemplateResponse(
        request,
        "partials/archivo_fila.html",
        {"archivo": archivo},
    )


@router.delete("/archivos/{archivo_id}", response_class=HTMLResponse)
async def borrar_archivo(
    archivo_id: int,
    db: Session = Depends(get_db),
    _sesion: dict = Depends(requerir_profesor_o_admin),
):
    archivo = db.query(Archivo).filter(Archivo.id == archivo_id).first()
    if archivo is not None:
        eliminar_archivo_storage(archivo.url_archivo)
        db.delete(archivo)
        db.commit()

    return HTMLResponse(content="", status_code=status.HTTP_200_OK)


@router.get("/archivos/{archivo_id}/previsualizar", response_class=HTMLResponse)
async def previsualizar_archivo(
    request: Request,
    archivo_id: int,
    db: Session = Depends(get_db),
    _sesion: dict = Depends(requerir_cualquier_rol),
):
    archivo = db.query(Archivo).filter(Archivo.id == archivo_id).first()
    clasificacion = clasificar_archivo(archivo.tipo, archivo.url_archivo) if archivo else {}

    return templates.TemplateResponse(
        request,
        "partials/archivo_previsualizacion.html",
        {"archivo": archivo, **clasificacion},
    )


# ---------------------------------------------------------------------------
# ADMIN (todas las rutas exigen sesion de admin; el admin_id nunca se toma
# de la URL, siempre se calcula desde la sesion via requerir_admin)
# ---------------------------------------------------------------------------

def obtener_contexto_admin(db: Session, admin_id: int) -> dict:
    return {
        "admin_id": admin_id,
        "archivos_institucionales": obtener_archivos_institucionales(db),
        "usuarios": obtener_usuarios_gestionables(db),
        "grados": obtener_todos_los_grados(db),
    }


def obtener_usuarios_gestionables(db: Session) -> list[dict]:
    usuarios = (
        db.query(Usuario)
        .filter(Usuario.rol.in_(["estudiante", "profesor"]))
        .order_by(Usuario.correo.asc())
        .all()
    )

    resultado = []
    for usuario in usuarios:
        nombre = None
        grado = None

        if usuario.rol == "estudiante":
            perfil = db.query(Estudiante).filter(Estudiante.id_usuario == usuario.id).first()
            if perfil:
                nombre = perfil.nombre
                grado = perfil.grado
        elif usuario.rol == "profesor":
            perfil = db.query(Profesor).filter(Profesor.id_usuario == usuario.id).first()
            if perfil:
                nombre = perfil.nombre

        resultado.append({
            "usuario": usuario,
            "nombre": nombre or "(sin nombre)",
            "grado": grado,
        })

    return resultado


@router.get("/admin", response_class=HTMLResponse)
async def admin_inicio(
    request: Request,
    admin_id: int = Depends(requerir_admin),
    db: Session = Depends(get_db),
):
    contexto = obtener_contexto_admin(db, admin_id)
    return templates.TemplateResponse(
        request,
        "pages/admin.html",
        {
            **contexto,
            "panel_activo": "institucional",
        },
    )


@router.get("/admin/panel/{panel}", response_class=HTMLResponse)
async def admin_panel(
    request: Request,
    panel: str,
    admin_id: int = Depends(requerir_admin),
    db: Session = Depends(get_db),
):
    contexto = obtener_contexto_admin(db, admin_id)
    plantillas = {
        "institucional": "partials/admin_institucional.html",
        "usuarios": "partials/admin_usuarios.html",
        "proyecto": "partials/admin_proyecto.html",
    }

    plantilla = plantillas.get(panel, plantillas["institucional"])
    return templates.TemplateResponse(
        request,
        plantilla,
        {
            **contexto,
            "panel_activo": panel,
        },
    )


@router.post("/admin/institucional/archivos", response_class=HTMLResponse)
async def subir_archivo_institucional(
    request: Request,
    nombre: str = Form(...),
    descripcion: str = Form(""),
    archivo: UploadFile = File(...),
    admin_id: int = Depends(requerir_admin),
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter(Admin.id == admin_id).first()

    error = None
    if admin is None or admin.id_usuario is None:
        error = "No se encontro un usuario asociado a este administrador, no se pudo subir el archivo."
    else:
        contenido = await archivo.read()
        url_publica = subir_archivo_storage(
            contenido,
            archivo.filename or "archivo",
            "institucional",
            content_type=archivo.content_type,
        )

        nuevo_archivo = Archivo(
            nombre=nombre.strip() or (archivo.filename or "Archivo sin nombre"),
            tipo=archivo.content_type or "application/octet-stream",
            descripcion=descripcion.strip(),
            url_archivo=url_publica,
            id_usuario=admin.id_usuario,
            id_materia=None,
            id_grado=None,
        )
        db.add(nuevo_archivo)
        db.commit()

    return templates.TemplateResponse(
        request,
        "partials/admin_institucional.html",
        {
            "admin_id": admin_id,
            "archivos_institucionales": obtener_archivos_institucionales(db),
            "error_subida": error,
        },
    )


@router.post("/admin/usuarios", response_class=HTMLResponse)
async def crear_usuario(
    request: Request,
    rol: str = Form(...),
    nombre: str = Form(...),
    correo: str = Form(...),
    contrasena: str = Form(...),
    id_grado: int | None = Form(None),
    admin_id: int = Depends(requerir_admin),
    db: Session = Depends(get_db),
):
    rol = rol.strip().lower()
    correo_limpio = correo.strip().lower()
    error = None

    if rol not in ("estudiante", "profesor"):
        error = "Rol invalido."
    elif db.query(Usuario).filter(Usuario.correo == correo_limpio).first() is not None:
        error = "Ya existe un usuario con ese correo."
    else:
        nuevo_usuario = Usuario(
            correo=correo_limpio,
            contrasena=contrasena,
            rol=rol,
        )
        db.add(nuevo_usuario)
        db.flush()  # para obtener nuevo_usuario.id antes del commit

        if rol == "estudiante":
            perfil = Estudiante(
                id_usuario=nuevo_usuario.id,
                nombre=nombre.strip(),
                id_grado=id_grado,
            )
            db.add(perfil)
            db.flush()
            nuevo_usuario.id_estudiante = perfil.id
        else:
            perfil = Profesor(
                id_usuario=nuevo_usuario.id,
                nombre=nombre.strip(),
            )
            db.add(perfil)
            db.flush()
            nuevo_usuario.id_profesor = perfil.id

        db.commit()

    return templates.TemplateResponse(
        request,
        "partials/admin_usuarios.html",
        {
            "admin_id": admin_id,
            "usuarios": obtener_usuarios_gestionables(db),
            "grados": obtener_todos_los_grados(db),
            "error_usuario": error,
        },
    )


@router.get("/admin/usuarios/{usuario_id}/editar", response_class=HTMLResponse)
async def obtener_edicion_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    _admin_id: int = Depends(requerir_admin),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    nombre = ""
    id_grado_actual = None

    if usuario is not None:
        if usuario.rol == "estudiante":
            perfil = db.query(Estudiante).filter(Estudiante.id_usuario == usuario.id).first()
            if perfil:
                nombre = perfil.nombre
                id_grado_actual = perfil.id_grado
        elif usuario.rol == "profesor":
            perfil = db.query(Profesor).filter(Profesor.id_usuario == usuario.id).first()
            if perfil:
                nombre = perfil.nombre

    return templates.TemplateResponse(
        request,
        "partials/admin_editar_usuario.html",
        {
            "usuario": usuario,
            "nombre": nombre,
            "id_grado_actual": id_grado_actual,
            "grados": obtener_todos_los_grados(db),
        },
    )


@router.post("/admin/usuarios/{usuario_id}/editar", response_class=HTMLResponse)
async def guardar_edicion_usuario(
    request: Request,
    usuario_id: int,
    nombre: str = Form(...),
    correo: str = Form(...),
    contrasena: str = Form(""),
    id_grado: int | None = Form(None),
    db: Session = Depends(get_db),
    _admin_id: int = Depends(requerir_admin),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if usuario is not None:
        correo_limpio = correo.strip().lower()
        ya_existe = (
            db.query(Usuario)
            .filter(Usuario.correo == correo_limpio, Usuario.id != usuario.id)
            .first()
        )
        if ya_existe is None:
            usuario.correo = correo_limpio

        if contrasena.strip():
            usuario.contrasena = contrasena

        if usuario.rol == "estudiante":
            perfil = db.query(Estudiante).filter(Estudiante.id_usuario == usuario.id).first()
            if perfil:
                perfil.nombre = nombre.strip() or perfil.nombre
                perfil.id_grado = id_grado
        elif usuario.rol == "profesor":
            perfil = db.query(Profesor).filter(Profesor.id_usuario == usuario.id).first()
            if perfil:
                perfil.nombre = nombre.strip() or perfil.nombre

        db.commit()

    return templates.TemplateResponse(
        request,
        "partials/admin_fila_usuario.html",
        {"item": {
            "usuario": usuario,
            "nombre": nombre.strip() if usuario else None,
            "grado": (
                db.query(Grado).filter(Grado.id == id_grado).first()
                if usuario and usuario.rol == "estudiante" and id_grado
                else None
            ),
        }},
    )


@router.delete("/admin/usuarios/{usuario_id}", response_class=HTMLResponse)
async def borrar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _admin_id: int = Depends(requerir_admin),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is not None:
        db.delete(usuario)
        db.commit()

    return HTMLResponse(content="", status_code=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# ESTUDIANTE (todas las rutas exigen sesion de estudiante; el estudiante_id
# nunca se toma de la URL, siempre se calcula desde la sesion)
# ---------------------------------------------------------------------------

@router.get("/estudiante", response_class=HTMLResponse)
async def estudiante_inicio(
    request: Request,
    estudiante_id: int = Depends(requerir_estudiante),
    db: Session = Depends(get_db),
):
    contexto = obtener_contexto_estudiante(db, estudiante_id)
    return templates.TemplateResponse(
        request,
        "pages/estudiante.html",
        {
            **contexto,
            "panel_activo": "institucional",
        },
    )


@router.get("/estudiante/panel/{panel}", response_class=HTMLResponse)
async def estudiante_panel(
    request: Request,
    panel: str,
    estudiante_id: int = Depends(requerir_estudiante),
    db: Session = Depends(get_db),
):
    contexto = obtener_contexto_estudiante(db, estudiante_id)
    plantillas = {
        "institucional": "partials/estudiante_institucional.html",
        "materias": "partials/estudiante_materias.html",
        "archivos": "partials/estudiante_archivos.html",
        "proyecto": "partials/estudiante_proyecto.html",
    }

    plantilla = plantillas.get(panel, plantillas["institucional"])
    return templates.TemplateResponse(
        request,
        plantilla,
        {
            **contexto,
            "panel_activo": panel,
        },
    )


@router.get("/estudiante/materias/{materia_id}", response_class=HTMLResponse)
async def estudiante_materia_activa(
    request: Request,
    materia_id: int,
    estudiante_id: int = Depends(requerir_estudiante),
    db: Session = Depends(get_db),
):
    contexto = obtener_contexto_estudiante(db, estudiante_id)
    materia = db.query(Materia).filter(Materia.id == materia_id).first()
    id_grado = contexto["grado"].id if contexto["grado"] else None

    return templates.TemplateResponse(
        request,
        "partials/estudiante_materia_archivos.html",
        {
            **contexto,
            "materia_activa": materia,
            "archivos_materia": obtener_archivos_materia_grado(db, materia_id, id_grado),
        },
    )