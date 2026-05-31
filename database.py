import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Creamos el motor de la base de datos
engine = create_engine(DATABASE_URL)

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
