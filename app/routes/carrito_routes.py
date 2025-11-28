from flask import Blueprint, request, jsonify, render_template
from app.services.carrito_service import CarritoService

carrito_bp = Blueprint("carrito", __name__)

@carrito_bp.get("/carritos")
def obtener_todos_carritos():
    """Obtener todos los carritos"""
    return jsonify(CarritoService.obtener_todos())


@carrito_bp.get("/carrito/pagina")
def carrito_pagina():
    """Página visual del carrito (HTML)"""
    id_cliente = 1  # temporal hasta login

    carrito = CarritoService.obtener_con_detalles(id_cliente)

    detalles = carrito.get("Detalles", []) if isinstance(carrito, dict) else []
    total = sum([d["Subtotal"] for d in detalles])

    return render_template(
        "carrito/carrito.html",
        detalles=detalles,
        total=total,
        carrito_count=len(detalles)
    )


@carrito_bp.get("/carrito/<int:id_carrito>")
def obtener_carrito_por_id(id_carrito):
    resultado = CarritoService.obtener_por_id(id_carrito)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)


@carrito_bp.get("/carrito/cliente/<int:id_cliente>")
def obtener_carrito_cliente(id_cliente):
    resultado = CarritoService.obtener_carrito(id_cliente)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)


@carrito_bp.get("/carrito/cliente/<int:id_cliente>/completo")
def obtener_carrito_completo(id_cliente):
    resultado = CarritoService.obtener_con_detalles(id_cliente)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)


@carrito_bp.post("/carrito/cliente/<int:id_cliente>")
def crear_carrito(id_cliente):
    resultado = CarritoService.crear_carrito(id_cliente)
    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 201


@carrito_bp.post("/carrito/<int:id_cliente>/agregar/<int:id_producto>")
def agregar_producto(id_cliente, id_producto):
    resultado = CarritoService.agregar_producto(id_cliente, id_producto)

    if "error" in resultado:
        return jsonify(resultado), 400

    return jsonify(resultado), 201


@carrito_bp.put("/carrito/<int:id_carrito>")
def actualizar_carrito(id_carrito):
    data = request.json
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    resultado = CarritoService.actualizar(id_carrito, data)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)


@carrito_bp.delete("/carrito/<int:id_carrito>")
def eliminar_carrito(id_carrito):
    resultado = CarritoService.eliminar_carrito(id_carrito)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200


@carrito_bp.delete("/carrito/cliente/<int:id_cliente>")
def eliminar_carrito_cliente(id_cliente):
    resultado = CarritoService.eliminar_por_cliente(id_cliente)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200
