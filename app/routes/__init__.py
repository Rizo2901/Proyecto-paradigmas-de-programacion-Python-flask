from flask import Blueprint

def register_routes(app):
    from .main import main_bp
    app.register_blueprint(main_bp)
