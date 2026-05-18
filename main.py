from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="ATLAS")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

STUDENT_DATABASE = {
    "correo": "atlas@gmail.com",
    "password": "atlas123",
    "nombre": "sultano de tal",
    "grupo": "Grupo 11-3 - Programación",
}

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
    return templates.TemplateResponse(request, "pages/login.html",)


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    valid_login = (
        email.strip().lower() == STUDENT_DATABASE["correo"]
        and password == STUDENT_DATABASE["password"]
    )

    if not valid_login:
        return templates.TemplateResponse(
            request,
            "pages/login.html",
            {
                "error": "Revisa el correo y la contraseña. Usa los datos de ejemplo.",
            },
            status_code=401,
        )

    return RedirectResponse(url="/inicio", status_code=303)


@app.get("/inicio", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "student": STUDENT_DATABASE,
            "files": UPLOADED_FILES,
            "upload_message": None,
        },
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, archivo: UploadFile = File(...)):
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
        "pages/dashboard.html",
        {
            "student": STUDENT_DATABASE,
            "files": UPLOADED_FILES,
            "upload_message": f"{archivo.filename} se agrego correctamente.",
        },
    )
