from flask import Blueprint, request, jsonify, render_template
from app.services.carrito_service import CarritoService
from app.services.carrito_detalle_service import CarritoDetalleService
from app.extensions import db

facturacion_bp = Blueprint("facturacion", __name__)


@facturacion_bp.get("/facturacion/pagina")
def facturacion_pagina():
    """Página de facturación con los datos del carrito"""
    try:
        # Obtener carrito anónimo con detalles
        carrito = CarritoService.obtener_carrito_anonimo_con_detalles()
        
        if not isinstance(carrito, dict) or "error" in carrito:
            return render_template(
                "facturacion/facturacion.html",
                detalles=[],
                total=0,
                id_carrito=None,
                error="No se pudo cargar el carrito"
            )
        
        detalles = carrito.get("Detalles", [])
        
        # Agregar nombre del producto a cada detalle si no lo tiene
        from app.models.productos import Productos
        for detalle in detalles:
            if not detalle.get("NombreProducto"):
                producto = db.session.get(Productos, detalle.get("IdProducto"))
                if producto:
                    detalle["NombreProducto"] = producto.Nombre
        
        total = sum([d.get("Subtotal", 0) for d in detalles if isinstance(d, dict)])
        id_carrito = carrito.get("IdCarrito")
        
        return render_template(
            "facturacion/facturacion.html",
            detalles=detalles,
            total=total,
            id_carrito=id_carrito
        )
        
    except Exception as e:
        import traceback
        print(f"[facturacion] Error en facturacion_pagina: {str(e)}\n{traceback.format_exc()}")
        return render_template(
            "facturacion/facturacion.html",
            detalles=[],
            total=0,
            id_carrito=None,
            error=str(e)
        ), 500


@facturacion_bp.post("/facturacion/procesar")
def procesar_facturacion():
    """Procesa la facturación y crea el pedido"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Datos no proporcionados"}), 400
        
        id_carrito = data.get("IdCarrito")
        if not id_carrito:
            return jsonify({"error": "No se especificó el carrito"}), 400
        
        id_carrito = int(id_carrito)
        
        # Obtener detalles del carrito
        items = CarritoDetalleService.obtener_items(id_carrito)
        
        if not items:
            return jsonify({"error": "El carrito está vacío"}), 400
        
        # Calcular total
        total = sum([item.get("Subtotal", 0) for item in items])
        
        # Obtener o crear cliente con los datos de facturación
        from app.models.clientes import Clientes
        from app.models.pedidos import Pedidos
        from app.models.pedidos_detalle import PedidosDetalle
        from app.models.productos import Productos
        from decimal import Decimal
        
        # Construir nombre completo
        nombre = data.get("Nombre", "").strip()
        apellidos = data.get("Apellidos", "").strip()
        nombre_completo = f"{nombre} {apellidos}".strip() if nombre or apellidos else "Cliente"
        
        email = data.get("Email", "").strip()
        telefono = data.get("Telefono", "").strip()
        tienda_envio = data.get("TiendaEnvio", "").strip()
        notas = data.get("Notas", "").strip()
        
        # PASO 1: Obtener o crear cliente y hacer COMMIT
        if email:
            cliente = db.session.query(Clientes).filter(
                Clientes.Correo == email
            ).first()
            
            if not cliente:
                cliente = Clientes(
                    Nombre=nombre_completo,
                    Correo=email,
                    Telefono=telefono if telefono else None,
                    Direccion=notas if notas else None
                )
                db.session.add(cliente)
                db.session.commit()  # Guardar cliente inmediatamente
            else:
                # Actualizar datos del cliente existente
                if nombre_completo and nombre_completo != "Cliente":
                    cliente.Nombre = nombre_completo
                if telefono:
                    cliente.Telefono = telefono
                if notas:
                    cliente.Direccion = notas
                db.session.commit()
        else:
            # Usar cliente anónimo
            cliente = db.session.query(Clientes).filter(
                Clientes.Correo == "anonimo@tienda.local"
            ).first()
            
            if not cliente:
                cliente = Clientes(
                    Nombre="Cliente Anónimo",
                    Correo="anonimo@tienda.local"
                )
                db.session.add(cliente)
                db.session.commit()  # Guardar cliente inmediatamente
        
        # PASO 2: Crear el pedido (el cliente ya existe en la BD)
        # Intentar crear con todos los campos opcionales
        try:
            pedido = Pedidos(
                IdCliente=cliente.IdCliente,
                Total=Decimal(str(total)),
                Notas=notas if notas else None,
                TiendaEnvio=tienda_envio if tienda_envio else None
            )
        except Exception:
            # Si falla por columnas que no existen, crear sin ellas
            pedido = Pedidos(
                IdCliente=cliente.IdCliente,
                Total=Decimal(str(total))
            )
        db.session.add(pedido)
        db.session.commit()  # Guardar pedido
        
        # PASO 3: Reducir stock de los productos
        for item in items:
            id_producto = item.get("IdProducto")
            cantidad = item.get("Cantidad", 1)
            
            producto = db.session.get(Productos, id_producto)
            if producto and producto.Stock >= cantidad:
                producto.Stock -= cantidad
        
        db.session.commit()  # Guardar cambios de stock
        
        # PASO 4: Intentar crear los detalles del pedido (opcional, puede fallar)
        try:
            for item in items:
                id_producto = item.get("IdProducto")
                cantidad = item.get("Cantidad", 1)
                precio_unitario = item.get("PrecioUnitario", 0)
                
                detalle_pedido = PedidosDetalle(
                    IdPedido=pedido.IdPedido,
                    IdProducto=id_producto,
                    Cantidad=cantidad,
                    PrecioUnitario=Decimal(str(precio_unitario))
                )
                db.session.add(detalle_pedido)
            db.session.commit()
        except Exception as detalle_error:
            # Si falla crear detalles, no pasa nada (la tabla puede no existir)
            print(f"[facturacion] Nota: No se pudieron crear detalles del pedido: {str(detalle_error)}")
            db.session.rollback()
        
        # Limpiar el carrito después de crear el pedido
        CarritoDetalleService.limpiar_carrito_por_idcarrito(id_carrito)
        
        # Enviar correo de confirmación al cliente
        email_enviado = False
        if email and email != "anonimo@tienda.local":
            try:
                from app.services.email_service import EmailService
                resultado_email = EmailService.enviar_confirmacion_pedido(
                    email_destino=email,
                    nombre_cliente=nombre_completo or "Cliente",
                    id_pedido=pedido.IdPedido,
                    total=float(total),
                    detalles_items=items
                )
                email_enviado = resultado_email.get("success", False)
            except Exception as email_error:
                print(f"[facturacion] Error al enviar correo: {str(email_error)}")
                email_enviado = False
        
        return jsonify({
            "message": "Pedido creado exitosamente",
            "IdPedido": pedido.IdPedido,
            "Total": float(total),
            "Cliente": cliente.Nombre,
            "EmailEnviado": email_enviado
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[facturacion] Error en procesar_facturacion: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Error al procesar la facturación: {str(e)}"}), 500

