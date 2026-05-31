from pathlib import Path
from fastapi import FastAPI, File, Form, Request, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Componentes de conexión a Neon
from sqlalchemy.orm import Session
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


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "pages/login.html")


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request, 
    id: str = Form(...),       # El HTML envía 'email', pero aquí leerá el numero_identificacion
    password: str = Form(...),    # Lee 'contrasena'
    db: Session = Depends(get_db)  # Conexión a Neon
):
    # Convertimos la entrada a número entero ya que numero_identificacion ahora es BIGINT
    try:
        identificacion_ingresada = int(id.strip())
    except ValueError:
        return templates.TemplateResponse(
            request,
            "pages/login.html",
            {"error": "El número de identificación debe contener solo números."},
            status_code=400,
        )

    # Buscamos al estudiante en Neon utilizando el número de identificación
    usuario_encontrado = db.query(models.Usuario).filter(
        models.Usuario.numero_identificacion == identificacion_ingresada
    ).first()

    # Validamos si existe el usuario y si coincide la contraseña textual ingresada
    if usuario_encontrado and usuario_encontrado.contrasena == password:
        # Redireccionamos pasando el número de identificación en la URL para mantener el estado del usuario
        return RedirectResponse(url=f"/inicio?user_id={identificacion_ingresada}", status_code=303)

    return templates.TemplateResponse(
        request,
        "pages/login.html",
        {
            "error": "Revisa la identificación y la contraseña. Usa los datos de la base de datos.",
        },
        status_code=401,
    )


@app.get("/inicio", response_class=HTMLResponse)
async def home(request: Request, user_id: int = None, db: Session = Depends(get_db)):
    student_data = None
    
    if user_id:
        # Buscamos al estudiante con el ID provisto en la URL
        estudiante = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == user_id).first()
        
        if estudiante:
            # Armamos el diccionario dinámico respetando los nombres de variables que usa tu archivo HTML
            student_data = {
                "correo": str(estudiante.numero_identificacion),
                "nombre": estudiante.nombre,
                "grupo": f"Grupo {estudiante.grupo} - {estudiante.tecnica}",
            }

    # Si ocurre un acceso directo sin iniciar sesión, usamos un objeto temporal por seguridad
    if not student_data:
        student_data = {
            "correo": "No identificado",
            "nombre": "Invitado",
            "grupo": "Sin asignar",
        }

    return templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "student": student_data,
            "files": UPLOADED_FILES,
            "upload_message": None,
        },
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, user_id: int = None, archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    suffix = archivo.filename.rsplit(".", 1)[-1].upper() if "." in archivo.filename else "Archivo"
    UPLOADED_FILES.insert(
        0,
        {
            "nombre": archivo.filename,
            "tipo": suffix,
            "detalle": "Subido en esta sesion",
        },
    )

    # Recuperamos de nuevo al usuario en Neon para que el Navbar/Dashboard siga mostrando su información original
    student_data = None
    if user_id:
        estudiante = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == user_id).first()
        if estudiante:
            student_data = {
                "correo": str(estudiante.numero_identificacion),
                "nombre": estudiante.nombre,
                "grupo": f"Grupo {estudiante.grupo} - {estudiante.tecnica}",
            }

    if not student_data:
        student_data = {
            "correo": "No identificado",
            "nombre": "Invitado",
            "grupo": "Sin asignar",
        }

    return templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "student": student_data,
            "files": UPLOADED_FILES,
            "upload_message": f"{archivo.filename} se agrego correctamente.",
        },
    )
