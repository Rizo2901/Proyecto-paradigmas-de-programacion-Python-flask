import os
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_SERVER = os.getenv("DB_SERVER")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DRIVER = os.getenv("DB_DRIVER")

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
        f"?driver={DB_DRIVER}"
    )
