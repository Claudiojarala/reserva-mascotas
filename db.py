import os
import bcrypt
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# --- CONFIGURACIÓN DE CONEXIÓN DE PRODUCCIÓN ---
DB_HOST = os.getenv("DB_HOST", "localhost")

if "proxy.rlwy.net" in DB_HOST or "postgres.railway.internal" in DB_HOST:
    if DB_HOST.startswith("postgresql://"):
        DATABASE_URL = DB_HOST.replace("postgresql://", "postgresql+psycopg2://")
    elif DB_HOST.startswith("postgres://"):
        DATABASE_URL = DB_HOST.replace("postgres://", "postgresql+psycopg2://")
    else:
        DATABASE_URL = DB_HOST
else:
    DATABASE_URL = f"postgresql+psycopg2://postgres:password_seguro@{DB_HOST}:5432/guarderia_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==============================================================================
# CAPA DE SEGURIDAD 1: Cifrado en Reposo con Fernet (AES-128)
# Reemplaza el cifrado XOR académico por uno criptográficamente seguro.
# En producción, FERNET_KEY debe estar en una variable de entorno secreta.
# ==============================================================================
_fernet_key_env = os.getenv("FERNET_KEY")
if _fernet_key_env:
    # Se asegura de convertir el string a bytes para dárselo a Fernet
    FERNET_KEY = _fernet_key_env.encode()
else:
    # Si no existe en Railway, se genera una válida temporal en memoria
    from cryptography.fernet import Fernet
    FERNET_KEY = Fernet.generate_key()

fernet = Fernet(FERNET_KEY)

def cifrar_dato(texto: str) -> str:
    """Cifra un texto plano usando Fernet (AES-128 CBC + HMAC). Retorna string base64."""
    if not texto:
        return ""
    return fernet.encrypt(texto.encode()).decode()

def descifrar_dato(texto_cifrado: str) -> str:
    """Descifra un texto previamente cifrado con Fernet. Retorna el texto original."""
    if not texto_cifrado:
        return ""
    try:
        return fernet.decrypt(texto_cifrado.encode()).decode()
    except Exception:
        return "[Error al descifrar]"

# ==============================================================================
# CAPA DE SEGURIDAD 2: Autenticación con bcrypt + JWT
# 5 usuarios registrados. Las contraseñas NUNCA se guardan en texto plano,
# solo sus hashes generados con bcrypt.hashpw().
#
# Credenciales de acceso:
#   Usuario      | Contraseña
#   -------------|----------------
#   boris        | admin123
#   claudio      | guarderia2024
#   ana          | exotica55
#   marcos       | faunasegura9
#   valentina    | reptil2025
# ==============================================================================
USUARIOS = {
    "boris": {
        "password_hash": b"$2b$12$7Pbm8fWqWjg9.MqrXiB9.OIvBJGbt6CJvsgYU7hrzMMZGgzAn7wQi",
        "rol": "admin"
    },
    "claudio": {
        "password_hash": b"$2b$12$VjFimxJ6G7rc1kpNcRIYLeB0VVodmJSANeuQ3jV2KUAOzz70/FhnW",
        "rol": "admin"
    },
    "ana": {
        "password_hash": b"$2b$12$bVvpWiJ3NGpIw2W4COLu1.efWrvUe3qko7UajH5wfL1qEVIOJk8nW",
        "rol": "admin"
    },
    "marcos": {
        "password_hash": b"$2b$12$j0mEJHzC88KZcRG10a3on.Aw6M2nHJmE0UWRGq5LmoOrtAoG/Jl72",
        "rol": "admin"
    },
    "valentina": {
        "password_hash": b"$2b$12$5Thdu4Myur0kjRFSxL.JJ.e.46fhTpDfekP06rmzq6RV1TduGGTYm",
        "rol": "admin"
    },
}

def verificar_credenciales(usuario: str, password: str) -> bool:
    """
    Verifica si el usuario existe y si la contraseña coincide con el hash bcrypt.
    Retorna True si las credenciales son válidas.
    """
    if usuario not in USUARIOS:
        return False
    hash_guardado = USUARIOS[usuario]["password_hash"]
    return bcrypt.checkpw(password.encode(), hash_guardado)

# ==============================================================================
# CAPA DE DATOS: Modelos Relacionales (ORM con SQLAlchemy)
# Sin cambios respecto al diseño original de Claudio.
# ==============================================================================
class Dueno(Base):
    __tablename__ = 'duenos'
    id_dueno         = Column(Integer, primary_key=True, index=True)
    nombre           = Column(String(100), nullable=False)
    correo_cifrado   = Column(String, nullable=False)
    telefono_cifrado = Column(String, nullable=False)

    mascotas = relationship("Mascota", back_populates="dueno", cascade="all, delete-orphan")


class Mascota(Base):
    __tablename__ = 'mascotas'
    id_mascota     = Column(Integer, primary_key=True, index=True)
    id_dueno       = Column(Integer, ForeignKey('duenos.id_dueno', ondelete='CASCADE'))
    nombre_mascota = Column(String(100), nullable=False)
    especie        = Column(String(100), nullable=False)

    dueno    = relationship("Dueno", back_populates="mascotas")
    reservas = relationship("Reserva", back_populates="mascota", cascade="all, delete-orphan")


class Reserva(Base):
    __tablename__ = 'reservas'
    id_reserva        = Column(Integer, primary_key=True)
    id_mascota        = Column(Integer, ForeignKey('mascotas.id_mascota', ondelete='CASCADE'))
    fecha_ingreso     = Column(Date, nullable=False)
    dieta_restriccion = Column(String, nullable=False)

    mascota = relationship("Mascota", back_populates="reservas")


def inicializar_base_de_datos():
    """Crea todas las tablas en PostgreSQL si aún no existen."""
    Base.metadata.create_all(bind=engine)
