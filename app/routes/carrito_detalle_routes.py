from flask import Blueprint, request, jsonify, render_template
from app.services.carrito_detalle_service import CarritoDetalleService

carrito_detalle_bp = Blueprint("carrito_detalle", __name__)

# Página visual del carrito detalle
@carrito_detalle_bp.get("/carrito_detalle/pagina")
def carrito_pagina():
    try:
        # obtener carrito anónimo (temporal hasta auth)
        from app.services.carrito_service import CarritoService
        carrito = CarritoService.obtener_carrito_anonimo_con_detalles()
        
        if not isinstance(carrito, dict):
            carrito = {"Detalles": [], "IdCarrito": None}
        elif "error" in carrito:
            carrito = {"Detalles": [], "IdCarrito": None}
            
        detalles = carrito.get("Detalles", [])
        total = sum([d.get("Subtotal", 0) for d in detalles if isinstance(d, dict)])
        productos = CarritoDetalleService.obtener_productos_disponibles()
        id_carrito = carrito.get("IdCarrito")

        return render_template(
            "carrito_detalle/carrito_detalle.html",
            detalles=detalles,
            total=total,
            carrito_count=len(detalles),
            productos=productos,
            id_carrito=id_carrito
        )
    except Exception as e:
        import traceback
        print(f"[carrito_detalle] Error en carrito_pagina: {str(e)}\n{traceback.format_exc()}")
        # Retornar página con datos vacíos en caso de error
        return render_template(
            "carrito_detalle/carrito_detalle.html",
            detalles=[],
            total=0,
            carrito_count=0,
            productos=[],
            id_carrito=None
        ), 500

# Obtener todos los detalles
@carrito_detalle_bp.get("/carrito_detalle/all")
def obtener_todos_detalles():
    return jsonify(CarritoDetalleService.obtener_todos())

# Obtener detalle por ID
@carrito_detalle_bp.get("/carrito_detalle/items/<int:id_carrito>")
def obtener_items_carrito(id_carrito):
    return jsonify(CarritoDetalleService.obtener_items(id_carrito))


@carrito_detalle_bp.get("/carrito_detalle/total")
def obtener_total_carrito():
    try:
        # temporal: obtener total para carrito anónimo
        from app.services.carrito_service import CarritoService
        carrito = CarritoService.obtener_carrito_anonimo_con_detalles()
        if not isinstance(carrito, dict) or "Detalles" not in carrito:
            return jsonify({"Total": 0, "Items": 0, "CantidadTotal": 0})
        detalles = carrito.get("Detalles", [])
        total = sum([d.get("Subtotal", 0) for d in detalles if isinstance(d, dict)])
        cantidad_total = sum([d.get("Cantidad", 0) for d in detalles if isinstance(d, dict)])
        return jsonify({"Total": total, "Items": len(detalles), "CantidadTotal": cantidad_total})
    except Exception as e:
        import traceback
        print(f"[carrito_detalle] Error en obtener_total_carrito: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"Total": 0, "Items": 0, "CantidadTotal": 0, "error": str(e)}), 500

@carrito_detalle_bp.post("/carrito_detalle/items/<int:id_carrito>")
def agregar_producto_carrito(id_carrito):
    # soporta JSON o form data (para envíos desde formularios HTML clásicos)
    data = request.get_json(silent=True)
    if not data:
        # request.form devuelve valores strings, convertir según se necesite
        form = request.form
        data = {
            "IdProducto": int(form.get("IdProducto")) if form.get("IdProducto") else None,
            "Cantidad": int(form.get("Cantidad")) if form.get("Cantidad") else 1
        }
    if not data or "IdProducto" not in data or data.get("IdProducto") is None:
        return jsonify({"error": "Datos incompletos"}), 400
    print(f"[carrito_detalle] POST add id_carrito={id_carrito} data={data}")
    resultado = CarritoDetalleService.agregar(id_carrito, data)
    # si hay error, devolver 400 y loguear
    if isinstance(resultado, dict) and "error" in resultado:
        print(f"[carrito_detalle] agregar error: {resultado}")
        return jsonify(resultado), 400
    return jsonify(resultado), 201


@carrito_detalle_bp.post("/carrito_detalle/items")
def agregar_producto_carrito_default():
    # Agregar producto en el carrito del cliente por defecto (1). Soporta JSON o form-data
    data = request.get_json(silent=True)
    if not data:
        form = request.form
        data = {
            "IdProducto": int(form.get("IdProducto")) if form.get("IdProducto") else None,
            "Cantidad": int(form.get("Cantidad")) if form.get("Cantidad") else 1
        }
    if not data or not data.get("IdProducto"):
        return jsonify({"error": "Datos incompletos"}), 400

    # obtener carrito anónimo o crear si no existe
    from app.services.carrito_service import CarritoService
    carrito = CarritoService.obtener_carrito_anonimo_con_detalles()
    if not isinstance(carrito, dict) or "error" in carrito:
        return jsonify(carrito if isinstance(carrito, dict) else {"error": "Error al obtener carrito"}), 400
    if "IdCarrito" not in carrito:
        # Si no tiene IdCarrito, intentar obtener el carrito anónimo directamente
        carrito_anonimo = CarritoService.obtener_carrito_anonimo()
        if "error" in carrito_anonimo:
            return jsonify(carrito_anonimo), 400
        id_carrito = carrito_anonimo.get("IdCarrito")
    else:
        id_carrito = carrito.get("IdCarrito")

    print(f"[carrito_detalle] POST add default id_carrito={id_carrito} data={data}")
    resultado = CarritoDetalleService.agregar(id_carrito, data)
    if isinstance(resultado, dict) and "error" in resultado:
        print(f"[carrito_detalle] agregar default error: {resultado}")
        return jsonify(resultado), 400
    return jsonify(resultado), 201

# Actualizar cantidad de un producto
@carrito_detalle_bp.put("/carrito_detalle/items/<int:id_detalle>")
def actualizar_item_carrito(id_detalle):
    data = request.json
    print(f"[carrito_detalle] PUT id_detalle={id_detalle} data={data}")
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    resultado = CarritoDetalleService.actualizar_por_detalle(id_detalle, data)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

# Eliminar producto por detalle
@carrito_detalle_bp.delete("/carrito_detalle/items/<int:id_detalle>")
def eliminar_item_carrito(id_detalle):
    resultado = CarritoDetalleService.eliminar_por_id(id_detalle)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200

# Limpiar carrito por IdCarrito
@carrito_detalle_bp.delete("/carrito_detalle/limpiar/<int:id_carrito>")
def limpiar_carrito(id_carrito):
    resultado = CarritoDetalleService.limpiar_carrito_por_idcarrito(id_carrito)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200


    