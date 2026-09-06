from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Grado(Base):
    __tablename__ = "grados"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    grupo = Column(String(50), nullable=False)

    # Relaciones
    estudiantes = relationship("Estudiante", back_populates="grado")
    registros_materias = relationship("MateriaGrado", back_populates="grado", cascade="all, delete-orphan")


class Materia(Base):
    __tablename__ = "materias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)

    # Relaciones
    registros_grados = relationship("MateriaGrado", back_populates="materia", cascade="all, delete-orphan")
    registros_profesores = relationship("ProfesorMateria", back_populates="materia", cascade="all, delete-orphan")


class MateriaGrado(Base):
    __tablename__ = "materia_grado"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_materia = Column(Integer, ForeignKey('materias.id', ondelete='CASCADE'), nullable=False)
    id_grado = Column(Integer, ForeignKey('grados.id', ondelete='CASCADE'), nullable=False)

    # Relaciones
    materia = relationship("Materia", back_populates="registros_grados")
    grado = relationship("Grado", back_populates="registros_materias")


class ProfesorMateria(Base):
    __tablename__ = "profesor_materia"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_profesor = Column(Integer, ForeignKey('profesor.id', ondelete='CASCADE'), nullable=False)
    id_materia = Column(Integer, ForeignKey('materias.id', ondelete='CASCADE'), nullable=False)

    # Relaciones
    profesor = relationship("Profesor", back_populates="registros_materias")
    materia = relationship("Materia", back_populates="registros_profesores")


class Archivo(Base):
    __tablename__ = "archivos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    tipo = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    grupo = Column(String(50), nullable=True)
    url_archivo = Column(Text, nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    id_materia = Column(Integer, ForeignKey("materias.id", ondelete="CASCADE"), nullable=True)
    id_grado = Column(Integer, ForeignKey("grados.id", ondelete="CASCADE"), nullable=True)
    fecha_subida = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="archivos")
    materia = relationship("Materia")
    grado = relationship("Grado")


class Estudiante(Base):
    __tablename__ = "estudiante"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=True)
    nombre = Column(String(150), nullable=False)
    id_grado = Column(Integer, ForeignKey("grados.id", ondelete="SET NULL"), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    grado = relationship("Grado", back_populates="estudiantes")


class Profesor(Base):
    __tablename__ = "profesor"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=True)
    nombre = Column(String(150), nullable=False)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    registros_materias = relationship("ProfesorMateria", back_populates="profesor", cascade="all, delete-orphan")


class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[id_usuario])


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_estudiante = Column(Integer, ForeignKey("estudiante.id", ondelete="SET NULL"), nullable=True)
    id_profesor = Column(Integer, ForeignKey("profesor.id", ondelete="SET NULL"), nullable=True)
    id_admin = Column(Integer, ForeignKey("admin.id", ondelete="SET NULL"), nullable=True)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)

    # Relaciones
    archivos = relationship("Archivo", back_populates="usuario", cascade="all, delete-orphan")