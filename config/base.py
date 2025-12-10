import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_SERVER = os.getenv("DB_SERVER")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    if not all([DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD]):
        raise ValueError("Faltan variables de entorno para la conexión a la BD")

    # Normalizar el driver: reemplazar + por espacios si vienen del .env
    driver_normalized = DB_DRIVER.replace("+", " ")
    driver_encoded = quote_plus(driver_normalized)
    
    # DEBUG: Verificar valores (quitar después)
    print(f"DEBUG - DB_USER: {DB_USER}")
    print(f"DEBUG - DB_PASSWORD length: {len(DB_PASSWORD) if DB_PASSWORD else 0}")
    print(f"DEBUG - DB_SERVER: {DB_SERVER}")
    print(f"DEBUG - DB_NAME: {DB_NAME}")
    print(f"DEBUG - DB_DRIVER original: {DB_DRIVER}")
    print(f"DEBUG - DB_DRIVER normalizado: {driver_normalized}")
    
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_SERVER}/{DB_NAME}"
        f"?driver={driver_encoded}"
        f"&TrustServerCertificate=yes"
    )
    
    # DEBUG: Mostrar URI (sin contraseña completa por seguridad)
    print(f"DEBUG - URI (sin password): {SQLALCHEMY_DATABASE_URI.split('@')[0]}@...")
