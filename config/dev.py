from .base import BaseConfig
import os

class DevConfig(BaseConfig):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_SERVER')}/{os.getenv('DB_NAME')}?"
        f"driver={os.getenv('DB_DRIVER').replace(' ', '+')}"
    )
