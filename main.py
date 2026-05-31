from pathlib import Path
from fastapi import FastAPI, File, Form, Request, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Importamos lo necesario para conectar con Neon
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
import models

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="ATLAS")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

UPLOADED_FILES = [
    {"nombre": "Guia de estudio", "tipo": "PDF", "detalle": "Semana 4"},
    {"nombre": "Actividad 2", "tipo": "Entrega", "detalle": "Viernes"},
    {"nombre": "Lectura 1", "tipo": "Articulo", "detalle": "12 paginas"},
    {"nombre": "Video clase", "tipo": "MP4", "detalle": "18 min"},
    {"nombre": "Rubrica", "tipo": "PDF", "detalle": "Evaluacion"},
    {"nombre": "Proyecto final", "tipo": "Carpeta", "detalle": "Activo"},
]

GROUP_FILES = [
    {"nombre": "Plan de trabajo grupal", "tipo": "PDF", "detalle": "Compartido"},
    {"nombre": "Acta de reunion", "tipo": "DOCX", "detalle": "Ultima sesion"},
    {"nombre": "Material de apoyo", "tipo": "Carpeta", "detalle": "Grupo actual"},
]


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "pages/login.html")


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request, 
    identificacion: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(get_db) # Conexión a Neon
):
    identificacion_ingresada = identificacion.strip()

    if db is None:
        return templates.TemplateResponse(
            request,
            "pages/login.html",
            {
                "error": "La conexion con la base de datos no esta configurada en el servidor.",
            },
            status_code=503,
        )

    try:
        # Buscamos al usuario directamente en la base de datos Neon
        usuario_encontrado = db.query(models.Usuario).filter(
            models.Usuario.numero_identificacion == identificacion_ingresada
        ).first()
    except SQLAlchemyError:
        return templates.TemplateResponse(
            request,
            "pages/login.html",
            {
                "error": "No se pudo conectar con la base de datos. Revisa DATABASE_URL en Vercel.",
            },
            status_code=503,
        )

    # Validamos si existe y si coincide la contraseña
    if usuario_encontrado and usuario_encontrado.clave == password:
        return RedirectResponse(url=f"/inicio?user_id={identificacion_ingresada}", status_code=303)

    return templates.TemplateResponse(
        request,
        "pages/login.html",
        {
            "error": "Revisa la identificación y la contraseña.",
        },
        status_code=401,
    )


@app.get("/inicio", response_class=HTMLResponse)
async def home(request: Request, user_id: str = None, db: Session = Depends(get_db)):
    # Buscamos los datos del estudiante en Neon para pintarlos en el Dashboard
    estudiante = None
    if user_id and db is not None:
        try:
            estudiante = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == user_id).first()
        except SQLAlchemyError:
            estudiante = None

    # Si por alguna razón no se encuentra, mandamos un diccionario vacío o por defecto
    identificacion_estudiante = estudiante.numero_identificacion if estudiante else "Invitado"
    student_data = {
        "nombre": "Estudiante",
        "grupo": "Grupo actual",
        "identificacion": identificacion_estudiante,
    }

    return templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "student": student_data,
            "files": UPLOADED_FILES,
            "group_files": GROUP_FILES,
            "upload_message": None,
        },
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, user_id: str = None, archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    suffix = archivo.filename.rsplit(".", 1)[-1].upper() if "." in archivo.filename else "Archivo"
    UPLOADED_FILES.insert(
        0,
        {
            "nombre": archivo.filename,
            "tipo": suffix,
            "detalle": "Subido en esta sesion",
        },
    )

    # Volvemos a buscar al estudiante para no perder la información al renderizar la vista
    estudiante = None
    if user_id and db is not None:
        try:
            estudiante = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == user_id).first()
        except SQLAlchemyError:
            estudiante = None
        
    identificacion_estudiante = estudiante.numero_identificacion if estudiante else "Invitado"
    student_data = {
        "nombre": "Estudiante",
        "grupo": "Grupo actual",
        "identificacion": identificacion_estudiante,
    }

    return templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "student": student_data,
            "files": UPLOADED_FILES,
            "group_files": GROUP_FILES,
            "upload_message": f"{archivo.filename} se agrego correctamente.",
        },
    )
