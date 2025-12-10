from app.routes.home import home_bp
from app.routes.productos_routes import productos_bp
from app.routes.clientes_routes import clientes_bp
from app.routes.pedidos_routes import pedidos_bp
from app.routes.carrito_routes import carrito_bp
from app.routes.carrito_detalle_routes import carrito_detalle_bp
from app.routes.facturacion_routes import facturacion_bp

def register_routes(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(carrito_detalle_bp)
    app.register_blueprint(facturacion_bp)