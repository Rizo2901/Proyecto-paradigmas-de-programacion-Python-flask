from flask import Blueprint, request, jsonify, render_template
from app.services.productos_service import ProductosService

productos_bp = Blueprint("productos", __name__)
@productos_bp.get("/cartas/pagina")
def pagina_clientes():
    """Página HTML para gestionar cartas"""
    return render_template("cartas/cartas.html")
@productos_bp.get("/productos")
def obtener_productos():
    return jsonify(ProductosService.obtener_todos())

@productos_bp.get("/productos/<int:id_producto>")
def obtener_producto(id_producto):
    return jsonify(ProductosService.obtener_por_id(id_producto))

@productos_bp.post("/productos")
def crear_producto():
    data = request.json
    return jsonify(ProductosService.crear(data)), 201

@productos_bp.put("/productos/<int:id_producto>")
def actualizar_producto(id_producto):
    data = request.json
    return jsonify(ProductosService.actualizar(id_producto, data))

@productos_bp.delete("/productos/<int:id_producto>")
def eliminar_producto(id_producto):
    """Eliminar un producto"""
    resultado = ProductosService.eliminar_fisico(id_producto)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200
