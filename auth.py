from fastapi import Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from modelos import Admin, Estudiante, Profesor, Usuario


class NoAutenticado(Exception):
    """
    Se lanza cuando no hay una sesion activa, o cuando el rol de la sesion
    no coincide con el que exige la ruta. Un manejador global (en main.py)
    la convierte en una redireccion a /login.
    """


def iniciar_sesion(request: Request, usuario: Usuario) -> None:
    """Guarda la identidad del usuario en una cookie de sesion firmada por el servidor."""
    request.session["usuario_id"] = usuario.id
    request.session["rol"] = (usuario.rol or "").strip().lower()


def cerrar_sesion(request: Request) -> None:
    request.session.clear()


def _obtener_sesion(request: Request) -> dict:
    usuario_id = request.session.get("usuario_id")
    rol = request.session.get("rol")
    if not usuario_id or not rol:
        raise NoAutenticado()
    return {"usuario_id": usuario_id, "rol": rol}


def requerir_roles(*roles_permitidos: str):
    """Dependencia generica: exige sesion activa con uno de los roles indicados."""

    def dependencia(request: Request) -> dict:
        sesion = _obtener_sesion(request)
        if sesion["rol"] not in roles_permitidos:
            raise NoAutenticado()
        return sesion

    return dependencia


def requerir_profesor(request: Request, db: Session = Depends(get_db)) -> int:
    """Exige sesion de profesor y devuelve el ID de su perfil (nunca el de la URL)."""
    sesion = requerir_roles("profesor")(request)
    profesor = db.query(Profesor).filter(Profesor.id_usuario == sesion["usuario_id"]).first()
    if profesor is None:
        raise NoAutenticado()
    return profesor.id


def requerir_estudiante(request: Request, db: Session = Depends(get_db)) -> int:
    """Exige sesion de estudiante y devuelve el ID de su perfil (nunca el de la URL)."""
    sesion = requerir_roles("estudiante")(request)
    estudiante = db.query(Estudiante).filter(Estudiante.id_usuario == sesion["usuario_id"]).first()
    if estudiante is None:
        raise NoAutenticado()
    return estudiante.id


def requerir_admin(request: Request, db: Session = Depends(get_db)) -> int:
    """Exige sesion de administrador y devuelve el ID de su perfil (nunca el de la URL)."""
    sesion = requerir_roles("admin")(request)
    admin = db.query(Admin).filter(Admin.id_usuario == sesion["usuario_id"]).first()
    if admin is None:
        raise NoAutenticado()
    return admin.id


def requerir_profesor_o_admin(request: Request) -> dict:
    """Para rutas compartidas (editar/borrar archivos): profesor o admin, no estudiante."""
    return requerir_roles("profesor", "admin")(request)


def requerir_cualquier_rol(request: Request) -> dict:
    """Para rutas compartidas de solo lectura (previsualizar): cualquier sesion valida."""
    return requerir_roles("profesor", "admin", "estudiante")(request)