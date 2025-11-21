from flask import Blueprint, jsonify
from services.carrito_service import CarritoService

carrito_bp = Blueprint("carrito", __name__)

@carrito_bp.get("/carrito/<int:id_cliente>")
def obtener_carrito(id_cliente):
    return jsonify(CarritoService.obtener_carrito(id_cliente))

@carrito_bp.post("/carrito/<int:id_cliente>")
def crear_carrito(id_cliente):
    return jsonify(CarritoService.crear_carrito(id_cliente)), 201

@carrito_bp.delete("/carrito/<int:id_carrito>")
def eliminar_carrito(id_carrito):
    return jsonify(CarritoService.eliminar_carrito(id_carrito))
