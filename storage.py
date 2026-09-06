import os
import uuid

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # usa la service_role key, NUNCA la expongas al frontend
BUCKET_NAME = os.getenv("SUPABASE_BUCKET", "archivos")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Faltan SUPABASE_URL o SUPABASE_KEY en el archivo .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def subir_archivo_storage(contenido: bytes, nombre_original: str, carpeta: str, content_type: str | None = None) -> str:
    """
    Sube el archivo al bucket de Supabase Storage y devuelve la URL publica.

    `carpeta` agrupa los archivos dentro del bucket, por ejemplo:
    "materia_3/grado_2"
    """
    extension = nombre_original.rsplit(".", 1)[-1] if "." in nombre_original else "bin"
    nombre_unico = f"{uuid.uuid4().hex}.{extension}"
    ruta = f"{carpeta}/{nombre_unico}"

    supabase.storage.from_(BUCKET_NAME).upload(
        ruta,
        contenido,
        {"content-type": content_type or "application/octet-stream"},
    )

    resultado = supabase.storage.from_(BUCKET_NAME).get_public_url(ruta)

    # Segun la version de supabase-py, get_public_url puede devolver un str
    # o un dict con la llave "publicUrl". Cubrimos ambos casos.
    if isinstance(resultado, dict):
        return resultado.get("publicUrl") or resultado.get("public_url")
    return resultado


def eliminar_archivo_storage(url_archivo: str) -> None:
    """Elimina un archivo del bucket a partir de su URL publica guardada en la BD."""
    marcador = f"/{BUCKET_NAME}/"
    if marcador not in url_archivo:
        return
    ruta = url_archivo.split(marcador, 1)[1]
    supabase.storage.from_(BUCKET_NAME).remove([ruta])