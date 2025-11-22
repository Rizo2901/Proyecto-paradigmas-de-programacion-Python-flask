from flask import Blueprint, request, jsonify, render_template
from app.services.clientes_service import ClientesService

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.get("/clientes")
def obtener_clientes():
    """Obtener todos los clientes"""
    return jsonify(ClientesService.obtener_todos())

@clientes_bp.get("/clientes/pagina")
def pagina_clientes():
    """Página HTML para gestionar clientes"""
    return render_template("clientes/clientes.html")

@clientes_bp.get("/clientes/<int:id_cliente>")
def obtener_cliente(id_cliente):
    """Obtener un cliente por ID"""
    resultado = ClientesService.obtener_por_id(id_cliente)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@clientes_bp.get("/clientes/buscar/<correo>")
def buscar_cliente_por_correo(correo):
    """Buscar cliente por correo electrónico"""
    resultado = ClientesService.buscar_por_correo(correo)
    if not resultado:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify(resultado)

@clientes_bp.post("/clientes")
def crear_cliente():
    """Crear un nuevo cliente"""
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    resultado = ClientesService.crear(data)
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 201

@clientes_bp.put("/clientes/<int:id_cliente>")
def actualizar_cliente(id_cliente):
    """Actualizar un cliente existente"""
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    resultado = ClientesService.actualizar(id_cliente, data)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@clientes_bp.delete("/clientes/<int:id_cliente>")
def eliminar_cliente(id_cliente):
    """Eliminar un cliente"""
    resultado = ClientesService.eliminar(id_cliente)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200
