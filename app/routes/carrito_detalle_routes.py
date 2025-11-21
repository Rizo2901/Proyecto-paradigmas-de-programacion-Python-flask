from flask import Blueprint, request, jsonify
from services.carrito_detalle_service import CarritoDetalleService

carrito_detalle_bp = Blueprint("carrito_detalle", __name__)

@carrito_detalle_bp.get("/carrito/<int:id_cliente>/detalle")
def obtener_detalle(id_cliente):
    return jsonify(CarritoDetalleService.obtener_items(id_cliente))

@carrito_detalle_bp.post("/carrito/<int:id_cliente>/detalle")
def agregar_producto(id_cliente):
    data = request.json
    return jsonify(CarritoDetalleService.agregar(id_cliente, data)), 201

@carrito_detalle_bp.put("/carrito/<int:id_cliente>/detalle/<int:id_producto>")
def actualizar_cantidad(id_cliente, id_producto):
    data = request.json
    return jsonify(CarritoDetalleService.actualizar(id_cliente, id_producto, data))

@carrito_detalle_bp.delete("/carrito/<int:id_cliente>/detalle/<int:id_producto>")
def eliminar_item(id_cliente, id_producto):
    return jsonify(CarritoDetalleService.eliminar(id_cliente, id_producto))
