import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./atlas.db"

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Creamos el motor de la base de datos
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Sesión local para interactuar con la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para nuestros modelos
Base = declarative_base()

# Dependencia para abrir/cerrar la BD en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
