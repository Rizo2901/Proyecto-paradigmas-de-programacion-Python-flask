from flask import Blueprint, request, jsonify
from services.clientes_service import ClientesService

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.get("/clientes")
def obtener_clientes():
    return jsonify(ClientesService.obtener_todos())

@clientes_bp.get("/clientes/<int:id_cliente>")
def obtener_cliente(id_cliente):
    return jsonify(ClientesService.obtener_por_id(id_cliente))

@clientes_bp.post("/clientes")
def crear_cliente():
    data = request.json
    return jsonify(ClientesService.crear(data)), 201

@clientes_bp.put("/clientes/<int:id_cliente>")
def actualizar_cliente(id_cliente):
    data = request.json
    return jsonify(ClientesService.actualizar(id_cliente, data))

@clientes_bp.delete("/clientes/<int:id_cliente>")
def eliminar_cliente(id_cliente):
    return jsonify(ClientesService.eliminar(id_cliente))
