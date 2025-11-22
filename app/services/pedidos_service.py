from app.extensions import db
from app.models.pedidos import Pedidos
from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle
from app.models.productos import Productos
from decimal import Decimal

class PedidosService:

    @staticmethod
    def obtener_todos():
        """Obtener todos los pedidos"""
        pedidos = db.session.query(Pedidos).all()
        return [PedidosService.to_dict(p) for p in pedidos]

    @staticmethod
    def obtener_por_id(id_pedido):
        """Obtener un pedido por su ID"""
        pedido = db.session.query(Pedidos).get(id_pedido)
        if not pedido:
            return {"error": "Pedido no encontrado"}
        return PedidosService.to_dict(pedido)

    @staticmethod
    def obtener_pedidos(id_cliente):
        """Obtener todos los pedidos de un cliente"""
        pedidos = (
            db.session.query(Pedidos)
            .filter(Pedidos.IdCliente == id_cliente)
            .order_by(Pedidos.FechaPedido.desc())
            .all()
        )
        return [PedidosService.to_dict(p) for p in pedidos]

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

            # Calcular total
            total = Decimal(0)
            for item in items:
                producto = db.session.query(Productos).get(item.IdProducto)
                if not producto or producto.Stock < item.Cantidad:
                    return {"error": f"Stock insuficiente para {producto.Nombre if producto else 'producto'}"}
                
                subtotal = Decimal(item.Cantidad) * (item.PrecioUnitario or producto.Precio)
                total += subtotal

            # Crear pedido
            pedido = Pedidos(
                IdCliente=id_cliente,
                Total=total,
                Estado="Pendiente"
            )
            db.session.add(pedido)
            db.session.flush()  # Para obtener el ID del pedido

            # Reducir stock de productos
            for item in items:
                producto = db.session.query(Productos).get(item.IdProducto)
                producto.Stock -= item.Cantidad

            # Eliminar carrito y sus detalles (CASCADE lo hará automáticamente)
            db.session.delete(carrito)

            db.session.commit()
            return PedidosService.to_dict(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear pedido: {str(e)}"}

    @staticmethod
    def crear(data):
        """Crear un pedido manualmente"""
        try:
            pedido = Pedidos(
                IdCliente=data.get("IdCliente"),
                Total=data.get("Total", 0),
                Estado=data.get("Estado", "Pendiente")
            )
            db.session.add(pedido)
            db.session.commit()
            return PedidosService.to_dict(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear pedido: {str(e)}"}

    @staticmethod
    def actualizar(id_pedido, data):
        """Actualizar un pedido existente"""
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}

            if "IdCliente" in data:
                pedido.IdCliente = data["IdCliente"]
            if "Total" in data:
                pedido.Total = data["Total"]
            if "Estado" in data:
                pedido.Estado = data["Estado"]

            db.session.commit()
            return PedidosService.to_dict(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar pedido: {str(e)}"}

    @staticmethod
    def eliminar(id_pedido):
        """Eliminar un pedido"""
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}

            db.session.delete(pedido)
            db.session.commit()
            return {"message": "Pedido eliminado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al eliminar pedido: {str(e)}"}

    @staticmethod
    def cambiar_estado(id_pedido, nuevo_estado):
        """Cambiar el estado de un pedido"""
        try:
            pedido = db.session.query(Pedidos).get(id_pedido)
            if not pedido:
                return {"error": "Pedido no encontrado"}

            pedido.Estado = nuevo_estado
            db.session.commit()
            return PedidosService.to_dict(pedido)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al cambiar estado: {str(e)}"}

    @staticmethod
    def obtener_por_estado(estado):
        """Obtener pedidos por estado"""
        pedidos = db.session.query(Pedidos).filter(
            Pedidos.Estado == estado
        ).all()
        return [PedidosService.to_dict(p) for p in pedidos]

    @staticmethod
    def to_dict(p):
        """Convertir modelo a diccionario"""
        return {
            "IdPedido": p.IdPedido,
            "IdCliente": p.IdCliente,
            "FechaPedido": str(p.FechaPedido),
            "Total": float(p.Total),
            "Estado": p.Estado
        }
