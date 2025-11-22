from flask import Blueprint, render_template
from app.services.productos_service import ProductosService
 
home_bp = Blueprint("home", __name__)
 
@home_bp.route("/")
def home():
    """Página principal que muestra todos los productos"""
    try:
        productos = ProductosService.obtener_activos()  # Solo productos activos
        return render_template("index.html", productos=productos or [])
    except Exception as e:
        # En desarrollo, muestra el error
        print(f"Error al obtener productos: {e}")
        return render_template("index.html", productos=[])