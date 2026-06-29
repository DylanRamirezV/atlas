from pathlib import Path
from fastapi import FastAPI, File, Form, Request, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models
import logging

# Configuramos logs para ver errores reales en la terminal si algo falla con Neon
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="ATLAS")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# INICIALIZACIÓN DE LISTA GLOBAL
UPLOADED_FILES = []

# Datos estáticos (ejemplo)
INSTITUTIONAL_FILES = [
    {"id": 1, "nombre": "Calendario academico", "tipo": "Comunicado", "detalle": "Actualizado hoy"},
    {"id": 2, "nombre": "Normas institucionales", "tipo": "PDF", "detalle": "Version vigente"},
]

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "pages/login.html")

@app.post("/login")
async def login(
    request: Request, 
    id: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    try:
        # 1. Validar que el ID sea numérico
        try:
            user_id = int(id.strip())
        except ValueError:
            return templates.TemplateResponse(
                request, 
                "pages/login.html", 
                {"error": "El número de identificación debe contener solo números."}
            )

        # 2. Consultar en la base de datos de Neon
        usuario = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == user_id).first()
        
        # 3. Validar credenciales
        if usuario and usuario.contrasena == password:
            # --- SECCIÓN AÑADIDA: Redirección según el rol de la base de datos ---
            rol_usuario = usuario.rol.strip().lower() if usuario.rol else "estudiante"
            
            if rol_usuario == "profesor":
                response = RedirectResponse(url="/profesor#institucional", status_code=303)
            else:
                response = RedirectResponse(url="/inicio", status_code=303)
            # --------------------------------------------------------------------
            
            # path="/" y samesite="lax" para que las cookies viajen correctamente en los formularios POST
            response.set_cookie(
                key="user_id", 
                value=str(user_id), 
                httponly=True, 
                path="/", 
                samesite="lax"
            )
            return response
      
        return templates.TemplateResponse(
            request, 
            "pages/login.html", 
            {"error": "Identificación o contraseña incorrectas."}
        )
        
    except Exception as e:
        logger.error(f"Error crítico en el login: {str(e)}")
        return templates.TemplateResponse(
            request, 
            "pages/login.html", 
            {"error": f"Error de conexión con el servidor. Detalles: {str(e)}"}
        )


@app.get("/inicio", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id: 
        return RedirectResponse(url="/", status_code=303)

    estudiante = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == int(user_id)).first()
    if not estudiante: 
        return RedirectResponse(url="/", status_code=303)

    # FILTRADO ESTRICTO DE ARCHIVOS
    # Convertimos el alcance a minúsculas y limpiamos espacios para evitar duplicación entre pestañas
    mis_personales = [
        f for f in UPLOADED_FILES 
        if f.get("owner_id") == estudiante.numero_identificacion 
        and str(f.get("alcance")).strip().lower() == "personal"
    ]
    
    mis_grupales = [
        f for f in UPLOADED_FILES 
        if f.get("grupo") == estudiante.grupo 
        and str(f.get("alcance")).strip().lower() == "grupal"
    ]

    return templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "student": {
                "nombre": estudiante.nombre, 
                "grupo": estudiante.grupo, 
                "tecnica": estudiante.tecnica,
                "correo": str(estudiante.numero_identificacion)
            },
            "files": mis_personales,         # Va a la sección Personal en el HTML
            "group_files": mis_grupales,     # Va a la sección Grupal en el HTML
            "institutional_files": INSTITUTIONAL_FILES
        }
    )

@app.post("/upload")
async def upload_file(
    request: Request, 
    archivo: UploadFile = File(...), 
    destino: str = Form(...), 
    db: Session = Depends(get_db)
):
    try:
        # 1. Recuperamos la cookie 'user_id'
        user_id = request.cookies.get("user_id")
        if not user_id: 
            return RedirectResponse(url="/", status_code=303)

        # 2. Consultamos al usuario exacto en la base de datos Neon
        persona = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == int(user_id)).first()
        if not persona: 
            return RedirectResponse(url="/", status_code=303)

        # 3. Extraemos el rol limpiando cualquier espacio o mayúscula
        rol_usuario = "estudiante"
        if hasattr(persona, 'rol') and persona.rol:
            rol_usuario = str(persona.rol).strip().lower()

        # 4. Si el archivo viene vacío, abortamos y devolvemos al panel que corresponde
        if not archivo or not archivo.filename:
            url_retorno = "/profesor" if rol_usuario == "profesor" else "/inicio"
            return RedirectResponse(url=f"{url_retorno}?error=no_file", status_code=303)

        # 5. Construimos el nuevo objeto del archivo para la lista global
        alcance_limpio = str(destino).strip().lower()
        nuevo_archivo = {
            "nombre": archivo.filename,
            "owner_id": persona.numero_identificacion,
            "grupo": persona.grupo,
            "alcance": alcance_limpio 
        }
        
        global UPLOADED_FILES
        UPLOADED_FILES.insert(0, nuevo_archivo)
        
        # 6. REDIRECCIÓN ABSOLUTA: Si el rol es estrictamente profesor, va a /profesor
        # Para cualquier otra cosa (incluyendo 'estudiante'), va obligatoriamente a /inicio
        if rol_usuario == "profesor":
            return RedirectResponse(url="/profesor#docente-programacion", status_code=303)
        else:
            return RedirectResponse(url="/inicio", status_code=303)

    except Exception as e:
        print(f"--- ERROR CRÍTICO EN RUTA UPLOAD: {str(e)} ---")
        # En caso de un fallo inesperado, lo enviamos a /inicio por seguridad si está logueado
        return RedirectResponse(url="/inicio", status_code=303)


@app.post("/delete")
async def delete_file(
    request: Request, 
    nombre_archivo: str = Form(...), 
    db: Session = Depends(get_db)
):
    user_id = request.cookies.get("user_id")
    if not user_id: 
        return RedirectResponse(url="/", status_code=303)

    # Buscamos al usuario en Neon para verificar sus permisos reales
    usuario = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == int(user_id)).first()
    if not usuario: 
        return RedirectResponse(url="/", status_code=303)

    rol_actual = usuario.rol.strip().lower() if hasattr(usuario, 'rol') and usuario.rol else "estudiante"
    global UPLOADED_FILES
    
    # Recorremos la lista global para buscar el archivo por su nombre
    for archivo in UPLOADED_FILES:
        if archivo.get("nombre") == nombre_archivo:
            
            # REGLA DE SEGURIDAD OPTIMIZADA:
            # Condición 1: El usuario es PROFESOR (Borra lo que sea sin restricciones)
            # Condición 2: El usuario es dueño de un archivo personal
            # Condición 3: El usuario comparte grupo con un archivo grupal
            if (rol_actual == "profesor") or \
               (archivo.get("alcance") == "personal" and archivo.get("owner_id") == usuario.numero_identificacion) or \
               (archivo.get("alcance") == "grupal" and archivo.get("grupo") == usuario.grupo):
                
                UPLOADED_FILES.remove(archivo)
                break 

    # REDIRECCIÓN INTELIGENTE: Devolvemos al usuario a su respectivo panel
    if rol_actual == "profesor":
        return RedirectResponse(url="/profesor#docente-programacion", status_code=303)
    else:
        return RedirectResponse(url="/inicio", status_code=303)

@app.get("/logout")
async def logout():
    # 1. Creamos la redirección hacia la página de login (raíz)
    response = RedirectResponse(url="/", status_code=303)
    
    # 2. Eliminamos la cookie 'user_id' pasándole exactamente el mismo 'path="/"'
    response.delete_cookie(key="user_id", path="/")
    
    return response

@app.get("/profesor", response_class=HTMLResponse)
async def professor_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        user_id = request.cookies.get("user_id")
        if not user_id: 
            return RedirectResponse(url="/", status_code=303)

        profesor_db = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == int(user_id)).first()
        
        if not profesor_db:
            return RedirectResponse(url="/", status_code=303)
            
        rol_actual = profesor_db.rol.strip().lower() if hasattr(profesor_db, 'rol') and profesor_db.rol else "estudiante"
        if rol_actual != "profesor": 
            return RedirectResponse(url="/", status_code=303)

        # Estructura con los datos del docente
        teacher_data = {
            "nombre": profesor_db.nombre,
            "grupo": f"Docente - {profesor_db.tecnica if profesor_db.tecnica else 'Coordinación'}",
            "correo": str(profesor_db.numero_identificacion),
            "tecnica": profesor_db.tecnica if profesor_db.tecnica else "Coordinación"
        }

        # BLINDAJE ABSOLUTO CON 'file' INCLUIDO
        return templates.TemplateResponse(
            request, 
            "pages/teacher.html", 
            context={
                "request": request,
                "profesor": teacher_data,  
                "teacher": teacher_data,   
                "student": teacher_data,
                
                # --- DEFINICIÓN DE LA VARIABLE 'file' ---
                # Enviamos un objeto vacío por defecto para saciar al HTML
                "file": {
                    "nombre": "Ninguno",
                    "tipo": "Ninguno",
                    "detalle": "Ninguno"
                },
                # ----------------------------------------
                
                "all_files": UPLOADED_FILES,
                "institutional_files": INSTITUTIONAL_FILES  
            }
        )

    except Exception as e:
        print(f"--- ERROR CRÍTICO EN DASHBOARD PROFESOR: {str(e)} ---")
        return HTMLResponse(content=f"Error al cargar el panel del profesor: {str(e)}", status_code=500)
    
@app.post("/profesor/institucional/subir")
async def upload_institutional_file(
    request: Request,
    archivo: UploadFile = File(...),
    detalle: str = Form(...),
    nombre: str = Form(None), # El nombre es opcional en tu HTML
    db: Session = Depends(get_db)
):
    try:
        # 1. Seguridad: Verificar que el usuario esté logueado y sea profesor
        user_id = request.cookies.get("user_id")
        if not user_id:
            return RedirectResponse(url="/", status_code=303)

        profesor = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == int(user_id)).first()
        if not profesor or profesor.rol.strip().lower() != "profesor":
            return RedirectResponse(url="/", status_code=303)

        # 2. Validación de archivo
        if not archivo or not archivo.filename:
            return RedirectResponse(url="/profesor?error=no_file#institucional", status_code=303)

        # 3. Determinar el nombre visible (si no escribió ninguno, usamos el nombre real del archivo)
        nombre_visible = nombre.strip() if nombre and nombre.strip() else archivo.filename

        # 4. Obtener el tipo de archivo automáticamente leyendo su extensión
        tipo_archivo = archivo.filename.rsplit(".", 1)[-1].upper() if "." in archivo.filename else "DOCUMENTO"

        # 5. Generar un ID único simple para poder gestionarlo o editarlo después
        global INSTITUTIONAL_FILES
        nuevo_id = max([f["id"] for f in INSTITUTIONAL_FILES]) + 1 if INSTITUTIONAL_FILES else 1

        # 6. Construir el nuevo objeto institucional
        nuevo_recurso = {
            "id": nuevo_id,
            "nombre": nombre_visible,
            "tipo": tipo_archivo,
            "detalle": detalle.strip()
        }

        # Insertar al inicio de la lista institucional
        INSTITUTIONAL_FILES.insert(0, nuevo_recurso)

        # 7. Redirección limpia manteniendo al profesor parado en la pestaña institucional
        return RedirectResponse(url="/profesor#institucional", status_code=303)

    except Exception as e:
        print(f"--- ERROR AL SUBIR ARCHIVO INSTITUCIONAL: {str(e)} ---")
        return RedirectResponse(url="/profesor#institucional", status_code=303)

@app.post("/profesor/institucional/editar")
async def edit_institutional_file(
    request: Request,
    file_id: int = Form(...),    # Recibe el ID oculto del archivo
    nombre: str = Form(...),     # Recibe el nuevo nombre modificado
    tipo: str = Form(...),       # Recibe el nuevo tipo modificado
    detalle: str = Form(...),    # Recibe el nuevo detalle modificado
    db: Session = Depends(get_db)
):
    try:
        # 1. Seguridad: Verificar que el usuario tenga sesión activa y sea profesor
        user_id = request.cookies.get("user_id")
        if not user_id:
            return RedirectResponse(url="/", status_code=303)

        profesor = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == int(user_id)).first()
        if not profesor or profesor.rol.strip().lower() != "profesor":
            return RedirectResponse(url="/", status_code=303)

        # 2. Modificar la lista global de archivos institucionales
        global INSTITUTIONAL_FILES
        
        for archivo in INSTITUTIONAL_FILES:
            if archivo.get("id") == file_id:
                # Actualizamos los campos con los nuevos valores del formulario
                archivo["nombre"] = nombre.strip()
                archivo["tipo"] = tipo.strip()
                archivo["detalle"] = detalle.strip()
                break # Salimos del bucle al encontrar el archivo correspondiente

        # 3. Redirección limpia manteniendo al profesor en la sección institucional
        return RedirectResponse(url="/profesor#institucional", status_code=303)

    except Exception as e:
        print(f"--- ERROR AL EDITAR ARCHIVO INSTITUCIONAL: {str(e)} ---")
        return RedirectResponse(url="/profesor#institucional", status_code=303)

@app.post("/profesor/institucional/eliminar")
async def delete_institutional_file(
    request: Request,
    file_id: int = Form(...),    # Recibe el ID oculto del archivo a eliminar
    db: Session = Depends(get_db)
):
    try:
        # 1. Seguridad: Verificar que el usuario tenga sesión activa y sea profesor
        user_id = request.cookies.get("user_id")
        if not user_id:
            return RedirectResponse(url="/", status_code=303)

        profesor = db.query(models.Usuario).filter(models.Usuario.numero_identificacion == int(user_id)).first()
        if not profesor or profesor.rol.strip().lower() != "profesor":
            return RedirectResponse(url="/", status_code=303)

        # 2. Modificar la lista global sacando el archivo que coincida con el ID
        global INSTITUTIONAL_FILES
        
        for archivo in INSTITUTIONAL_FILES:
            if archivo.get("id") == file_id:
                INSTITUTIONAL_FILES.remove(archivo)
                break # Salimos del bucle una vez eliminado el elemento

        # 3. Redirección limpia manteniendo al profesor en la sección institucional
        return RedirectResponse(url="/profesor#institucional", status_code=303)

    except Exception as e:
        print(f"--- ERROR AL ELIMINAR ARCHIVO INSTITUCIONAL: {str(e)} ---")
        return RedirectResponse(url="/profesor#institucional", status_code=303)

