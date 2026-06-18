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

INSTITUTIONAL_FILES = [
    {"id": 1, "nombre": "Calendario academico", "tipo": "Comunicado", "detalle": "Actualizado hoy"},
    {"id": 2, "nombre": "Normas institucionales", "tipo": "PDF", "detalle": "Version vigente"},
    {"id": 3, "nombre": "Bienestar estudiantil", "tipo": "Informacion", "detalle": "Servicios disponibles"},
]

TEACHER_ACCOUNTS = {
    987654321: {
        "nombre": "Profesor ATLAS",
        "grupo": "Docente",
        "contrasena": "profesor1",
    }
}


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "pages/login.html")


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    code: str = Form(...),
    role: str = Form(...),
):
    codigo_valido = code.strip()
    if not codigo_valido.isdigit() or len(codigo_valido) != 9:
        return templates.TemplateResponse(
            request,
            "pages/login.html",
            {"error": "El código debe ser un número de 9 dígitos."},
            status_code=400,
        )

    if codigo_valido != "123456789":
        return templates.TemplateResponse(
            request,
            "pages/login.html",
            {"error": "Código incorrecto. Usa 123456789."},
            status_code=401,
        )

    if role not in {"student", "professor", "admin"}:
        return templates.TemplateResponse(
            request,
            "pages/login.html",
            {"error": "Selecciona Estudiante, Profesor o Administrador."},
            status_code=400,
        )

    if role == "admin":
        return RedirectResponse(url="/admin", status_code=303)

    return RedirectResponse(url="/usuario", status_code=303)


@app.get("/usuario", response_class=HTMLResponse)
async def user_panel(request: Request):
    return templates.TemplateResponse(request, "pages/usuario.html", {})


@app.post("/admin/upload", response_class=HTMLResponse)
async def admin_upload(request: Request, archivo: UploadFile = File(...)):
    suffix = archivo.filename.rsplit(".", 1)[-1].upper() if "." in archivo.filename else "Archivo"
    UPLOADED_FILES.insert(
        0,
        {
            "nombre": archivo.filename,
            "tipo": suffix,
            "detalle": "Subido en esta sesion",
        },
    )
    return templates.TemplateResponse(
        request,
        "pages/admin.html",
        {
            "message": f"{archivo.filename} se agregó correctamente.",
        },
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, message: str = None):
    return templates.TemplateResponse(request, "pages/admin.html", {"message": message})


@app.get("/inicio", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse(url="/usuario", status_code=303)


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
            "institutional_files": INSTITUTIONAL_FILES,
            "upload_message": f"{archivo.filename} se agrego correctamente.",
        },
    )


@app.get("/profesor", response_class=HTMLResponse)
async def teacher_dashboard(request: Request, teacher_id: int = None, message: str = None):
    teacher_data = get_teacher_data(teacher_id)

    return templates.TemplateResponse(
        request,
        "pages/teacher.html",
        {
            "student": teacher_data,
            "teacher": teacher_data,
            "institutional_files": INSTITUTIONAL_FILES,
            "message": message,
            "teacher_id": teacher_id,
        },
    )


@app.post("/profesor/institucional/subir", response_class=HTMLResponse)
async def teacher_upload_institutional(
    teacher_id: int = Form(None),
    archivo: UploadFile = File(...),
    nombre: str = Form(None),
    detalle: str = Form(...),
):
    suffix = archivo.filename.rsplit(".", 1)[-1].upper() if "." in archivo.filename else "Archivo"
    INSTITUTIONAL_FILES.insert(
        0,
        {
            "id": get_next_institutional_id(),
            "nombre": nombre or archivo.filename,
            "tipo": suffix,
            "detalle": detalle,
        },
    )
    return RedirectResponse(url=f"/profesor?teacher_id={teacher_id}&message=Archivo%20agregado", status_code=303)


@app.post("/profesor/institucional/editar", response_class=HTMLResponse)
async def teacher_edit_institutional(
    teacher_id: int = Form(None),
    file_id: int = Form(...),
    nombre: str = Form(...),
    tipo: str = Form(...),
    detalle: str = Form(...),
):
    institutional_file = find_institutional_file(file_id)
    if institutional_file:
        institutional_file["nombre"] = nombre
        institutional_file["tipo"] = tipo
        institutional_file["detalle"] = detalle

    return RedirectResponse(url=f"/profesor?teacher_id={teacher_id}&message=Archivo%20actualizado", status_code=303)


@app.post("/profesor/institucional/eliminar", response_class=HTMLResponse)
async def teacher_delete_institutional(
    teacher_id: int = Form(None),
    file_id: int = Form(...),
):
    global INSTITUTIONAL_FILES
    INSTITUTIONAL_FILES = [file for file in INSTITUTIONAL_FILES if file["id"] != file_id]
    return RedirectResponse(url=f"/profesor?teacher_id={teacher_id}&message=Archivo%20eliminado", status_code=303)


def get_teacher_data(teacher_id):
    teacher = TEACHER_ACCOUNTS.get(teacher_id)
    if not teacher:
        return {
            "nombre": "Profesor invitado",
            "grupo": "Docente",
        }

    return {
        "nombre": teacher["nombre"],
        "grupo": teacher["grupo"],
    }


def get_next_institutional_id():
    if not INSTITUTIONAL_FILES:
        return 1
    return max(file["id"] for file in INSTITUTIONAL_FILES) + 1


def find_institutional_file(file_id):
    for institutional_file in INSTITUTIONAL_FILES:
        if institutional_file["id"] == file_id:
            return institutional_file
    return None
