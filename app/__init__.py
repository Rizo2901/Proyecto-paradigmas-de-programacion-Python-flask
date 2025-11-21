from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_dict
from app.extensions import db

def create_app(config_name="dev"):
    app = Flask(__name__)

    app.config.from_object(config_dict[config_name])

    db.init_app(app)

    with app.app_context():
        from app.routes import register_routes
        register_routes(app)
        # db.create_all()  # Solo si quieres crear tablas automáticamente

    return app

