from app.extensions import db
from app.models.clientes import Clientes
from app.models.pedidos import Pedidos
from app.models.pedidos_detalle import PedidosDetalle
from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle

class ClientesService:

    @staticmethod
    def obtener_todos():
        """Obtener todos los clientes"""
        clientes = db.session.query(Clientes).all()
        return [ClientesService.to_dict(c) for c in clientes]

    @staticmethod
    def obtener_por_id(id_cliente):
        """Obtener un cliente por su ID"""
        cliente = db.session.query(Clientes).get(id_cliente)
        if not cliente:
            return {"error": "Cliente no encontrado"}
        return ClientesService.to_dict(cliente)

    @staticmethod
    def crear(data):
        """Crear un nuevo cliente"""
        try:
            cliente = Clientes(
                Nombre=data.get("Nombre"),
                Correo=data.get("Correo"),
                Telefono=data.get("Telefono"),
                Direccion=data.get("Direccion")
            )
            db.session.add(cliente)
            db.session.commit()
            return ClientesService.to_dict(cliente)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear cliente: {str(e)}"}

    @staticmethod
    def actualizar(id_cliente, data):
        """Actualizar un cliente existente"""
        try:
            cliente = db.session.query(Clientes).get(id_cliente)
            if not cliente:
                return {"error": "Cliente no encontrado"}

            if "Nombre" in data:
                cliente.Nombre = data["Nombre"]
            if "Correo" in data:
                cliente.Correo = data["Correo"]
            if "Telefono" in data:
                cliente.Telefono = data.get("Telefono")
            if "Direccion" in data:
                cliente.Direccion = data.get("Direccion")

            db.session.commit()
            return ClientesService.to_dict(cliente)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar cliente: {str(e)}"}

    @staticmethod
    def eliminar(id_cliente):
       
        try:
            cliente = db.session.query(Clientes).get(id_cliente)
            if not cliente:
                return {"error": "Cliente no encontrado"}

            # 1. Eliminar detalles de pedidos relacionados
            pedidos = db.session.query(Pedidos).filter(
                Pedidos.IdCliente == id_cliente
            ).all()
            
            for pedido in pedidos:
                # Eliminar detalles de cada pedido
                detalles_pedido = db.session.query(PedidosDetalle).filter(
                    PedidosDetalle.IdPedido == pedido.IdPedido
                ).all()
                for detalle in detalles_pedido:
                    db.session.delete(detalle)
                # Eliminar el pedido
                db.session.delete(pedido)

            # 2. Eliminar carritos y sus detalles
            carritos = db.session.query(Carrito).filter(
                Carrito.IdCliente == id_cliente
            ).all()
            
            for carrito in carritos:
                # Eliminar detalles de cada carrito
                detalles_carrito = db.session.query(CarritoDetalle).filter(
                    CarritoDetalle.IdCarrito == carrito.IdCarrito
                ).all()
                for detalle in detalles_carrito:
                    db.session.delete(detalle)
                # Eliminar el carrito
                db.session.delete(carrito)

            # 3. Finalmente eliminar el cliente
            db.session.delete(cliente)
            db.session.commit()
            return {"message": "Cliente eliminado correctamente"}
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            return {"error": f"Error al eliminar cliente: {error_msg}"}

    @staticmethod
    def buscar_por_correo(correo):
        """Buscar cliente por correo electrónico"""
        cliente = db.session.query(Clientes).filter(Clientes.Correo == correo).first()
        if not cliente:
            return None
        return ClientesService.to_dict(cliente)

    @staticmethod
    def to_dict(c):
        """Convertir modelo a diccionario"""
        return {
            "IdCliente": c.IdCliente,
            "Nombre": c.Nombre,
            "Correo": c.Correo,
            "Telefono": c.Telefono,
            "Direccion": c.Direccion,
            "FechaRegistro": str(c.FechaRegistro)
        }
