from app.extensions import db
from app.models.pedidos import Pedidos
from app.models.pedidos_detalle import PedidosDetalle
from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle
from app.models.productos import Productos
from decimal import Decimal

class PedidosService:

    @staticmethod
    def obtener_todos():
        """Obtener todos los pedidos"""
        pedidos = db.session.query(Pedidos).order_by(Pedidos.FechaPedido.desc()).all()
        return [PedidosService.to_dict_con_detalles(p) for p in pedidos]

    @staticmethod
    def obtener_por_id(id_pedido):
        """Obtener un pedido por su ID con sus detalles"""
        pedido = db.session.query(Pedidos).get(id_pedido)
        if not pedido:
            return {"error": "Pedido no encontrado"}
        return PedidosService.to_dict_con_detalles(pedido)

    @staticmethod
    def obtener_pedidos(id_cliente):
        """Obtener todos los pedidos de un cliente"""
        pedidos = (
            db.session.query(Pedidos)
            .filter(Pedidos.IdCliente == id_cliente)
            .order_by(Pedidos.FechaPedido.desc())
            .all()
        )
        return [PedidosService.to_dict_con_detalles(p) for p in pedidos]

    @staticmethod
    def crear_pedido(id_cliente):
        """Crear un pedido desde el carrito del cliente"""
        try:
            # Obtener el carrito del cliente
            carrito = db.session.query(Carrito).filter(
                Carrito.IdCliente == id_cliente
            ).first()

            if not carrito:
                return {"error": "El cliente no tiene carrito"}

            # Obtener items del carrito
            items = db.session.query(CarritoDetalle).filter(
                CarritoDetalle.IdCarrito == carrito.IdCarrito
            ).all()

            if not items:
                return {"error": "El carrito está vacío"}

            # Validar stock y calcular total
            total = Decimal(0)
            productos_validar = []
            
            for item in items:
                producto = db.session.query(Productos).get(item.IdProducto)
                if not producto:
                    return {"error": f"Producto con ID {item.IdProducto} no encontrado"}
                
                if not producto.Activo:
                    return {"error": f"El producto {producto.Nombre} no está activo"}
                
                if producto.Stock < item.Cantidad:
                    return {"error": f"Stock insuficiente para {producto.Nombre}. Stock disponible: {producto.Stock}, solicitado: {item.Cantidad}"}
                
                precio_unitario = item.PrecioUnitario or producto.Precio
                subtotal = Decimal(item.Cantidad) * Decimal(precio_unitario)
                total += subtotal
                
                productos_validar.append({
                    "producto": producto,
                    "cantidad": item.Cantidad,
                    "precio_unitario": precio_unitario
                })

            # Crear pedido (no especificar Estado para usar el valor por defecto de la BD)
            pedido = Pedidos(
                IdCliente=id_cliente,
                Total=total
                # Estado se omite para usar el server_default del modelo: N'Pendiente'
            )
            db.session.add(pedido)
            db.session.flush()  # Para obtener el ID del pedido

            # Crear detalles y reducir stock
            for item in productos_validar:
                detalle = PedidosDetalle(
                    IdPedido=pedido.IdPedido,
                    IdProducto=item["producto"].IdProducto,
                    Cantidad=item["cantidad"],
                    PrecioUnitario=item["precio_unitario"]
                )
                db.session.add(detalle)
                # Reducir stock
                item["producto"].Stock -= item["cantidad"]

            # Eliminar carrito y sus detalles (CASCADE lo hará automáticamente)
            db.session.delete(carrito)

            db.session.commit()
            return PedidosService.to_dict_con_detalles(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear pedido: {str(e)}"}

    @staticmethod
    def crear(data):
        """Crear un pedido manualmente con detalles"""
        try:
            detalles = data.get("detalles", [])
            if not detalles:
                return {"error": "El pedido debe tener al menos un detalle"}
            
            # Validar stock y calcular total
            total = Decimal(0)
            productos_validar = []
            
            for detalle in detalles:
                id_producto = detalle.get("IdProducto")
                cantidad = detalle.get("Cantidad", 1)
                
                producto = db.session.query(Productos).get(id_producto)
                if not producto:
                    return {"error": f"Producto con ID {id_producto} no encontrado"}
                
                if not producto.Activo:
                    return {"error": f"El producto {producto.Nombre} no está activo"}
                
                if producto.Stock < cantidad:
                    return {"error": f"Stock insuficiente para {producto.Nombre}. Stock disponible: {producto.Stock}, solicitado: {cantidad}"}
                
                precio_unitario = detalle.get("PrecioUnitario") or producto.Precio
                subtotal = Decimal(cantidad) * Decimal(precio_unitario)
                total += subtotal
                
                productos_validar.append({
                    "producto": producto,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario
                })
            
            # Crear pedido
            # Validar estado si se proporciona
            estado = data.get("Estado")
            estados_validos = ["Cancelado", "Entregado", "Enviado", "Pagado", "Pendiente"]
            
            if estado and estado not in estados_validos:
                return {"error": f"Estado inválido: {estado}. Estados válidos: {', '.join(estados_validos)}"}
            
            # No especificar Estado si no se proporciona, para usar el valor por defecto de la BD (N'Pendiente')
            pedido = Pedidos(
                IdCliente=data.get("IdCliente"),
                Total=total
            )
            # Solo establecer Estado si se proporcionó explícitamente y es válido
            if estado:
                pedido.Estado = estado
            db.session.add(pedido)
            db.session.flush()  # Para obtener el ID del pedido
            
            # Crear detalles y reducir stock
            for item in productos_validar:
                detalle = PedidosDetalle(
                    IdPedido=pedido.IdPedido,
                    IdProducto=item["producto"].IdProducto,
                    Cantidad=item["cantidad"],
                    PrecioUnitario=item["precio_unitario"]
                )
                db.session.add(detalle)
                # Reducir stock
                item["producto"].Stock -= item["cantidad"]
            
            db.session.commit()
            return PedidosService.to_dict_con_detalles(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear pedido: {str(e)}"}

    @staticmethod
    def actualizar(id_pedido, data):
        """Actualizar un pedido existente (solo información básica, no detalles)"""
        # Estados válidos según el CHECK constraint de la base de datos
        estados_validos = ["Cancelado", "Entregado", "Enviado", "Pagado", "Pendiente"]
        
        # Validar estado si se proporciona
        if "Estado" in data:
            estado = data["Estado"]
            if estado not in estados_validos:
                return {"error": f"Estado inválido: {estado}. Estados válidos: {', '.join(estados_validos)}"}
        
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}

            if "IdCliente" in data:
                pedido.IdCliente = data["IdCliente"]
            if "Estado" in data:
                pedido.Estado = data["Estado"]
            # El Total se recalcula automáticamente desde los detalles

            db.session.commit()
            return PedidosService.to_dict_con_detalles(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar pedido: {str(e)}"}

    @staticmethod
    def eliminar(id_pedido):
        """Eliminar un pedido y restaurar stock"""
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}

            # Restaurar stock de productos antes de eliminar
            detalles = db.session.query(PedidosDetalle).filter(
                PedidosDetalle.IdPedido == id_pedido
            ).all()
            
            for detalle in detalles:
                producto = db.session.query(Productos).get(detalle.IdProducto)
                if producto:
                    producto.Stock += detalle.Cantidad

            # Eliminar pedido (los detalles se eliminan por CASCADE)
            db.session.delete(pedido)
            db.session.commit()
            return {"message": "Pedido eliminado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al eliminar pedido: {str(e)}"}

    @staticmethod
    def cambiar_estado(id_pedido, nuevo_estado):
        """Cambiar el estado de un pedido"""
        # Estados válidos según el CHECK constraint de la base de datos
        estados_validos = ["Cancelado", "Entregado", "Enviado", "Pagado", "Pendiente"]
        
        if nuevo_estado not in estados_validos:
            return {"error": f"Estado inválido: {nuevo_estado}. Estados válidos: {', '.join(estados_validos)}"}
        
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}

            pedido.Estado = nuevo_estado
            db.session.commit()
            return PedidosService.to_dict_con_detalles(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al cambiar estado: {str(e)}"}

    @staticmethod
    def obtener_por_estado(estado):
        """Obtener pedidos por estado"""
        pedidos = db.session.query(Pedidos).filter(
            Pedidos.Estado == estado
        ).order_by(Pedidos.FechaPedido.desc()).all()
        return [PedidosService.to_dict_con_detalles(p) for p in pedidos]

    # Métodos para gestionar detalles de pedidos
    @staticmethod
    def obtener_detalles(id_pedido):
        """Obtener todos los detalles de un pedido"""
        detalles = db.session.query(PedidosDetalle).filter(
            PedidosDetalle.IdPedido == id_pedido
        ).all()
        return [PedidosService.detalle_to_dict(d) for d in detalles]

    @staticmethod
    def agregar_detalle(id_pedido, data):
        """Agregar un detalle a un pedido existente"""
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}
            
            if pedido.Estado not in ["Pendiente"]:
                return {"error": "Solo se pueden modificar pedidos en estado Pendiente"}

            id_producto = data.get("IdProducto")
            cantidad = data.get("Cantidad", 1)
            
            producto = db.session.query(Productos).get(id_producto)
            if not producto:
                return {"error": "Producto no encontrado"}
            
            if not producto.Activo:
                return {"error": f"El producto {producto.Nombre} no está activo"}
            
            # Verificar si ya existe el producto en el pedido
            detalle_existente = db.session.query(PedidosDetalle).filter(
                PedidosDetalle.IdPedido == id_pedido,
                PedidosDetalle.IdProducto == id_producto
            ).first()
            
            if detalle_existente:
                nueva_cantidad = detalle_existente.Cantidad + cantidad
                if producto.Stock < nueva_cantidad - detalle_existente.Cantidad:
                    return {"error": f"Stock insuficiente. Disponible: {producto.Stock}, necesario: {cantidad}"}
                
                producto.Stock -= cantidad  # Reducir solo la cantidad nueva
                detalle_existente.Cantidad = nueva_cantidad
                detalle_existente.PrecioUnitario = data.get("PrecioUnitario") or producto.Precio
            else:
                if producto.Stock < cantidad:
                    return {"error": f"Stock insuficiente para {producto.Nombre}. Disponible: {producto.Stock}, solicitado: {cantidad}"}
                
                detalle = PedidosDetalle(
                    IdPedido=id_pedido,
                    IdProducto=id_producto,
                    Cantidad=cantidad,
                    PrecioUnitario=data.get("PrecioUnitario") or producto.Precio
                )
                db.session.add(detalle)
                producto.Stock -= cantidad
            
            # Recalcular total del pedido
            PedidosService._recalcular_total(pedido)
            
            db.session.commit()
            return PedidosService.to_dict_con_detalles(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al agregar detalle: {str(e)}"}

    @staticmethod
    def actualizar_detalle(id_pedido, id_detalle, data):
        """Actualizar un detalle de pedido"""
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}
            
            if pedido.Estado not in ["Pendiente"]:
                return {"error": "Solo se pueden modificar pedidos en estado Pendiente"}

            detalle = db.session.query(PedidosDetalle).get(id_detalle)
            if not detalle or detalle.IdPedido != id_pedido:
                return {"error": "Detalle no encontrado"}

            producto = db.session.query(Productos).get(detalle.IdProducto)
            cantidad_anterior = detalle.Cantidad
            cantidad_nueva = data.get("Cantidad", cantidad_anterior)
            
            if cantidad_nueva != cantidad_anterior:
                diferencia = cantidad_nueva - cantidad_anterior
                stock_disponible = producto.Stock + cantidad_anterior  # Stock + lo que ya estaba reservado
                
                if stock_disponible < cantidad_nueva:
                    return {"error": f"Stock insuficiente. Disponible: {stock_disponible}, solicitado: {cantidad_nueva}"}
                
                producto.Stock += cantidad_anterior  # Restaurar stock anterior
                producto.Stock -= cantidad_nueva     # Reservar nueva cantidad
                detalle.Cantidad = cantidad_nueva
            
            if "PrecioUnitario" in data:
                detalle.PrecioUnitario = data["PrecioUnitario"]
            
            # Recalcular total del pedido
            PedidosService._recalcular_total(pedido)
            
            db.session.commit()
            return PedidosService.to_dict_con_detalles(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar detalle: {str(e)}"}

    @staticmethod
    def eliminar_detalle(id_pedido, id_detalle):
        """Eliminar un detalle de pedido"""
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}
            
            if pedido.Estado not in ["Pendiente"]:
                return {"error": "Solo se pueden modificar pedidos en estado Pendiente"}

            detalle = db.session.query(PedidosDetalle).get(id_detalle)
            if not detalle or detalle.IdPedido != id_pedido:
                return {"error": "Detalle no encontrado"}

            # Restaurar stock
            producto = db.session.query(Productos).get(detalle.IdProducto)
            if producto:
                producto.Stock += detalle.Cantidad

            # Eliminar detalle
            db.session.delete(detalle)
            
            # Recalcular total del pedido
            PedidosService._recalcular_total(pedido)
            
            db.session.commit()
            return PedidosService.to_dict_con_detalles(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al eliminar detalle: {str(e)}"}

    @staticmethod
    def _recalcular_total(pedido):
        """Recalcular el total de un pedido basado en sus detalles"""
        detalles = db.session.query(PedidosDetalle).filter(
            PedidosDetalle.IdPedido == pedido.IdPedido
        ).all()
        total = Decimal(0)
        for detalle in detalles:
            if detalle.Subtotal:
                total += detalle.Subtotal
            elif detalle.PrecioUnitario:
                total += Decimal(detalle.Cantidad) * Decimal(detalle.PrecioUnitario)
        pedido.Total = total

    @staticmethod
    def to_dict(p):
        """Convertir modelo a diccionario básico"""
        return {
            "IdPedido": p.IdPedido,
            "IdCliente": p.IdCliente,
            "FechaPedido": str(p.FechaPedido),
            "Total": float(p.Total),
            "Estado": p.Estado
        }

    @staticmethod
    def to_dict_con_detalles(p):
        """Convertir modelo a diccionario con detalles"""
        detalles = db.session.query(PedidosDetalle).filter(
            PedidosDetalle.IdPedido == p.IdPedido
        ).all()
        
        return {
            "IdPedido": p.IdPedido,
            "IdCliente": p.IdCliente,
            "FechaPedido": str(p.FechaPedido),
            "Total": float(p.Total),
            "Estado": p.Estado,
            "Detalles": [PedidosService.detalle_to_dict(d) for d in detalles]
        }

    @staticmethod
    def detalle_to_dict(d):
        """Convertir detalle a diccionario"""
        producto = db.session.query(Productos).get(d.IdProducto)
        return {
            "IdDetalle": d.IdDetalle,
            "IdPedido": d.IdPedido,
            "IdProducto": d.IdProducto,
            "NombreProducto": producto.Nombre if producto else "Producto no encontrado",
            "Cantidad": d.Cantidad,
            "PrecioUnitario": float(d.PrecioUnitario or 0),
            "Subtotal": float(d.Subtotal or 0)
        }
