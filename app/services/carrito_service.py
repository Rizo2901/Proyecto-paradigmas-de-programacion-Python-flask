from extensions import db
from models.carrito import Carrito

class CarritoService:

    @staticmethod
    def obtener_carrito(id_cliente):
        carrito = (
            db.session.query(Carrito)
            .filter(Carrito.IdCliente == id_cliente)
            .first()
        )

        if not carrito:
            return {"message": "El cliente no tiene carrito"}

        return {
            "IdCarrito": carrito.IdCarrito,
            "IdCliente": carrito.IdCliente,
            "FechaCreacion": str(carrito.FechaCreacion)
        }

    @staticmethod
    def crear_carrito(id_cliente):
        carrito = Carrito(IdCliente=id_cliente)
        db.session.add(carrito)
        db.session.commit()
        return {"message": "Carrito creado", "IdCarrito": carrito.IdCarrito}

    @staticmethod
    def eliminar_carrito(id_carrito):
        carrito = db.session.query(Carrito).get(id_carrito)
        if not carrito:
            return {"error": "Carrito no encontrado"}

        db.session.delete(carrito)
        db.session.commit()

        return {"message": "Carrito eliminado"}
