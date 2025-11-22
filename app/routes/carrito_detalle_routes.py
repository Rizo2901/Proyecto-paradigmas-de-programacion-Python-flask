from flask import Blueprint, request, jsonify
from app.services.carrito_detalle_service import CarritoDetalleService

carrito_detalle_bp = Blueprint("carrito_detalle", __name__)

@carrito_detalle_bp.get("/carrito-detalles")
def obtener_todos_detalles():
    """Obtener todos los detalles de carrito"""
    return jsonify(CarritoDetalleService.obtener_todos())

@carrito_detalle_bp.get("/carrito-detalle/<int:id_detalle>")
def obtener_detalle_por_id(id_detalle):
    """Obtener un detalle por su ID"""
    resultado = CarritoDetalleService.obtener_por_id(id_detalle)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@carrito_detalle_bp.get("/carrito/<int:id_cliente>/items")
def obtener_items_carrito(id_cliente):
    """Obtener items del carrito de un cliente"""
    return jsonify(CarritoDetalleService.obtener_items(id_cliente))

@carrito_detalle_bp.get("/carrito/<int:id_cliente>/total")
def obtener_total_carrito(id_cliente):
    """Obtener el total del carrito de un cliente"""
    return jsonify(CarritoDetalleService.obtener_total_carrito(id_cliente))

@carrito_detalle_bp.post("/carrito/<int:id_cliente>/items")
def agregar_producto_carrito(id_cliente):
    """Agregar un producto al carrito"""
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    if "IdProducto" not in data:
        return jsonify({"error": "IdProducto es requerido"}), 400
    
    resultado = CarritoDetalleService.agregar(id_cliente, data)
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 201

@carrito_detalle_bp.put("/carrito/<int:id_cliente>/items/<int:id_producto>")
def actualizar_item_carrito(id_cliente, id_producto):
    """Actualizar la cantidad de un producto en el carrito"""
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    resultado = CarritoDetalleService.actualizar(id_cliente, id_producto, data)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@carrito_detalle_bp.delete("/carrito/<int:id_cliente>/items/<int:id_producto>")
def eliminar_item_carrito(id_cliente, id_producto):
    """Eliminar un producto del carrito"""
    resultado = CarritoDetalleService.eliminar(id_cliente, id_producto)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200

@carrito_detalle_bp.delete("/carrito-detalle/<int:id_detalle>")
def eliminar_detalle_por_id(id_detalle):
    """Eliminar un detalle por su ID"""
    resultado = CarritoDetalleService.eliminar_por_id(id_detalle)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200

@carrito_detalle_bp.delete("/carrito/<int:id_cliente>/limpiar")
def limpiar_carrito(id_cliente):
    """Limpiar todos los productos del carrito"""
    resultado = CarritoDetalleService.limpiar_carrito(id_cliente)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200
