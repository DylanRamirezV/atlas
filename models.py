from sqlalchemy import Column, String
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    numero_identificacion = Column(String(50), primary_key=True, index=True)
    clave = Column(String(255), nullable=False)
