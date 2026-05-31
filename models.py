from sqlalchemy import Column, Integer, String, BigInteger
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    grupo = Column(String(20), nullable=False)
    tecnica = Column(String(100), nullable=False)
    numero_identificacion = Column(BigInteger, unique=True, nullable=False, index=True)
    contrasena = Column(String(255), nullable=False)
