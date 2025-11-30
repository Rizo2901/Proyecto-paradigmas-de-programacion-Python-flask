from flask import Blueprint, request, jsonify, render_template
from app.services.carrito_detalle_service import CarritoDetalleService

carrito_detalle_bp = Blueprint("carrito_detalle", __name__)

# Página visual del carrito detalle
@carrito_detalle_bp.get("/carrito_detalle/pagina")
def carrito_pagina():
    # obtener carrito para cliente 1 (temporal hasta auth)
    from app.services.carrito_service import CarritoService
    carrito = CarritoService.obtener_con_detalles(1)
    detalles = carrito.get("Detalles", []) if isinstance(carrito, dict) else []
    total = sum([d["Subtotal"] for d in detalles])
    productos = CarritoDetalleService.obtener_productos_disponibles()
    id_carrito = carrito.get("IdCarrito") if isinstance(carrito, dict) else None

    return render_template(
        "carrito_detalle/carrito_detalle.html",
        detalles=detalles,
        total=total,
        carrito_count=len(detalles),
        productos=productos
        , id_carrito=id_carrito
    )

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
    # temporal: obtener total para cliente 1
    from app.services.carrito_service import CarritoService
    carrito = CarritoService.obtener_con_detalles(1)
    if "Detalles" not in carrito:
        return jsonify({"Total": 0, "Items": 0, "CantidadTotal": 0})
    detalles = carrito.get("Detalles", [])
    total = sum([d["Subtotal"] for d in detalles])
    cantidad_total = sum([d["Cantidad"] for d in detalles])
    return jsonify({"Total": total, "Items": len(detalles), "CantidadTotal": cantidad_total})

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

    # obtener carrito o crear si no existe para cliente 1
    from app.services.carrito_service import CarritoService
    carrito = CarritoService.obtener_con_detalles(1)
    if "error" in carrito:
        return jsonify(carrito), 400
    if "IdCarrito" not in carrito:
        creado = CarritoService.crear_carrito(1)
        if "error" in creado:
            return jsonify(creado), 400
        id_carrito = creado.get("IdCarrito")
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


    