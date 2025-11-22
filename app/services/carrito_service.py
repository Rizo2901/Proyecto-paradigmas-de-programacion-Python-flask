from app.extensions import db
from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle

class CarritoService:

    @staticmethod
    def obtener_todos():
        """Obtener todos los carritos"""
        carritos = db.session.query(Carrito).all()
        return [CarritoService.to_dict(c) for c in carritos]

    @staticmethod
    def obtener_carrito(id_cliente):
        """Obtener el carrito de un cliente"""
        carrito = (
            db.session.query(Carrito)
            .filter(Carrito.IdCliente == id_cliente)
            .first()
        )

        if not carrito:
            return {"message": "El cliente no tiene carrito"}

        return CarritoService.to_dict(carrito)

    @staticmethod
    def obtener_por_id(id_carrito):
        """Obtener un carrito por su ID"""
        carrito = db.session.query(Carrito).get(id_carrito)
        if not carrito:
            return {"error": "Carrito no encontrado"}
        return CarritoService.to_dict(carrito)

    @staticmethod
    def crear_carrito(id_cliente):
        """Crear un nuevo carrito para un cliente"""
        try:
            # Verificar si ya existe un carrito
            carrito_existente = db.session.query(Carrito).filter(
                Carrito.IdCliente == id_cliente
            ).first()

            if carrito_existente:
                return {"error": "El cliente ya tiene un carrito", "IdCarrito": carrito_existente.IdCarrito}

            carrito = Carrito(IdCliente=id_cliente)
            db.session.add(carrito)
            db.session.commit()
            return CarritoService.to_dict(carrito)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear carrito: {str(e)}"}

    @staticmethod
    def actualizar(id_carrito, data):
        """Actualizar un carrito (solo IdCliente)"""
        try:
            carrito = db.session.query(Carrito).get(id_carrito)
            if not carrito:
                return {"error": "Carrito no encontrado"}

            if "IdCliente" in data:
                carrito.IdCliente = data["IdCliente"]

            db.session.commit()
            return CarritoService.to_dict(carrito)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar carrito: {str(e)}"}

    @staticmethod
    def eliminar_carrito(id_carrito):
        """Eliminar un carrito (CASCADE eliminará los detalles)"""
        try:
            carrito = db.session.query(Carrito).get(id_carrito)
            if not carrito:
                return {"error": "Carrito no encontrado"}

            db.session.delete(carrito)
            db.session.commit()
            return {"message": "Carrito eliminado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al eliminar carrito: {str(e)}"}

    @staticmethod
    def eliminar_por_cliente(id_cliente):
        """Eliminar el carrito de un cliente"""
        try:
            carrito = db.session.query(Carrito).filter(
                Carrito.IdCliente == id_cliente
            ).first()

            if not carrito:
                return {"error": "El cliente no tiene carrito"}

            db.session.delete(carrito)
            db.session.commit()
            return {"message": "Carrito eliminado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al eliminar carrito: {str(e)}"}

    @staticmethod
    def obtener_con_detalles(id_cliente):
        """Obtener carrito con sus detalles"""
        carrito = (
            db.session.query(Carrito)
            .filter(Carrito.IdCliente == id_cliente)
            .first()
        )

        if not carrito:
            return {"message": "El cliente no tiene carrito"}

        detalles = db.session.query(CarritoDetalle).filter(
            CarritoDetalle.IdCarrito == carrito.IdCarrito
        ).all()

        return {
            **CarritoService.to_dict(carrito),
            "Detalles": [
                {
                    "IdDetalle": d.IdDetalle,
                    "IdProducto": d.IdProducto,
                    "Cantidad": d.Cantidad,
                    "PrecioUnitario": float(d.PrecioUnitario or 0),
                    "Subtotal": float(d.Subtotal or 0)
                }
                for d in detalles
            ]
        }

    @staticmethod
    def to_dict(c):
        """Convertir modelo a diccionario"""
        return {
            "IdCarrito": c.IdCarrito,
            "IdCliente": c.IdCliente,
            "FechaCreacion": str(c.FechaCreacion)
        }
