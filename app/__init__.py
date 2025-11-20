from flask import Flask
from dotenv import load_dotenv
import os

from app.extensions import init_extensions
from app.routes import register_routes

load_dotenv()

def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "development")

    if env == "development":
        from config.dev import DevConfig
        app.config.from_object(DevConfig)
    else:
        from config.prod import ProdConfig
        app.config.from_object(ProdConfig)

    init_extensions(app)
    register_routes(app)

    return app
