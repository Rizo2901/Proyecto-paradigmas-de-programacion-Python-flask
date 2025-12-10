from flask import Blueprint, render_template
from app.services.productos_service import ProductosService
from app.services.carrito_service import CarritoService

home_bp = Blueprint("home", __name__)

@home_bp.route("/")
def home():
    """Página principal que muestra todos los productos"""
    try:
        productos = ProductosService.obtener_activos()  # Productos activos
        
        # Obtener carrito del cliente 1 (puedes cambiarlo después)
        carrito = CarritoService.obtener_con_detalles(1)
        carrito_count = len(carrito.get("Detalles", [])) if isinstance(carrito, dict) else 0

        return render_template(
            "index.html",
            productos=productos or [],
            carrito_count=carrito_count
        )

    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return render_template(
            "index.html",
            productos=[],
            carrito_count=0
        )
