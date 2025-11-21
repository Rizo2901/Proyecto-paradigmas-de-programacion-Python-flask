from flask import Blueprint, jsonify
from services.pedidos_service import PedidosService

pedidos_bp = Blueprint("pedidos", __name__)

@pedidos_bp.post("/pedidos/<int:id_cliente>")
def crear_pedido(id_cliente):
    return jsonify(PedidosService.crear_pedido(id_cliente)), 201

@pedidos_bp.get("/pedidos/<int:id_cliente>")
def obtener_pedidos(id_cliente):
    return jsonify(PedidosService.obtener_pedidos(id_cliente))

@pedidos_bp.get("/pedido/<int:id_pedido>")
def obtener_pedido(id_pedido):
    return jsonify(PedidosService.obtener_por_id(id_pedido))
