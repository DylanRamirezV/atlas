import os

from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from auth import NoAutenticado
from vistas import router as vistas_router

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "No se encontro la variable SECRET_KEY en el archivo .env. "
        "Es necesaria para firmar las cookies de sesion."
    )

app = FastAPI(title="Atlas")

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="atlas_session",
    same_site="lax",
    # https_only=True,  # activa esto cuando despliegues con HTTPS en produccion
)


@app.exception_handler(NoAutenticado)
async def manejar_no_autenticado(request, exc):
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(vistas_router)