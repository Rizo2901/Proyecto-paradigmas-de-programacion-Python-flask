from flask import Blueprint, request, jsonify, render_template
from app.services.pedidos_service import PedidosService

pedidos_bp = Blueprint("pedidos", __name__)

@pedidos_bp.get("/pedidos/pagina")
def pagina_pedidos():
    """Página HTML para gestionar pedidos"""
    return render_template("pedidos/pedidos.html")

@pedidos_bp.get("/pedidos")
def obtener_todos_pedidos():
    """Obtener todos los pedidos"""
    estado = request.args.get("estado")
    
    if estado:
        return jsonify(PedidosService.obtener_por_estado(estado))
    return jsonify(PedidosService.obtener_todos())

@pedidos_bp.get("/pedidos/<int:id_pedido>")
def obtener_pedido(id_pedido):
    """Obtener un pedido por ID"""
    resultado = PedidosService.obtener_por_id(id_pedido)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@pedidos_bp.get("/pedidos/cliente/<int:id_cliente>")
def obtener_pedidos_cliente(id_cliente):
    """Obtener todos los pedidos de un cliente"""
    return jsonify(PedidosService.obtener_pedidos(id_cliente))

@pedidos_bp.post("/pedidos/cliente/<int:id_cliente>")
def crear_pedido_desde_carrito(id_cliente):
    """Crear un pedido desde el carrito del cliente"""
    resultado = PedidosService.crear_pedido(id_cliente)
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 201

@pedidos_bp.post("/pedidos")
def crear_pedido_manual():
    """Crear un pedido manualmente"""
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    resultado = PedidosService.crear(data)
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 201

@pedidos_bp.put("/pedidos/<int:id_pedido>")
def actualizar_pedido(id_pedido):
    """Actualizar un pedido existente"""
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    resultado = PedidosService.actualizar(id_pedido, data)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@pedidos_bp.patch("/pedidos/<int:id_pedido>/estado")
def cambiar_estado_pedido(id_pedido):
    """Cambiar el estado de un pedido"""
    data = request.json
    if not data or "estado" not in data:
        return jsonify({"error": "Estado no proporcionado"}), 400
    
    resultado = PedidosService.cambiar_estado(id_pedido, data["estado"])
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@pedidos_bp.delete("/pedidos/<int:id_pedido>")
def eliminar_pedido(id_pedido):
    """Eliminar un pedido"""
    resultado = PedidosService.eliminar(id_pedido)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200

# Endpoints para gestionar detalles de pedidos
@pedidos_bp.get("/pedidos/<int:id_pedido>/detalles")
def obtener_detalles_pedido(id_pedido):
    """Obtener todos los detalles de un pedido"""
    resultado = PedidosService.obtener_detalles(id_pedido)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@pedidos_bp.post("/pedidos/<int:id_pedido>/detalles")
def agregar_detalle_pedido(id_pedido):
    """Agregar un detalle a un pedido"""
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    resultado = PedidosService.agregar_detalle(id_pedido, data)
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 201

@pedidos_bp.put("/pedidos/<int:id_pedido>/detalles/<int:id_detalle>")
def actualizar_detalle_pedido(id_pedido, id_detalle):
    """Actualizar un detalle de pedido"""
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    resultado = PedidosService.actualizar_detalle(id_pedido, id_detalle, data)
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado)

@pedidos_bp.delete("/pedidos/<int:id_pedido>/detalles/<int:id_detalle>")
def eliminar_detalle_pedido(id_pedido, id_detalle):
    """Eliminar un detalle de pedido"""
    resultado = PedidosService.eliminar_detalle(id_pedido, id_detalle)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200
