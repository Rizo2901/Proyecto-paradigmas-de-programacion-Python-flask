from extensions import db
from models.carrito_detalle import CarritoDetalle
from models.carrito import Carrito

class CarritoDetalleService:

    @staticmethod
    def obtener_items(id_cliente):
        carrito = (
            db.session.query(Carrito)
            .filter(Carrito.IdCliente == id_cliente)
            .first()
        )

        if not carrito:
            return []

        items = (
            db.session.query(CarritoDetalle)
            .filter(CarritoDetalle.IdCarrito == carrito.IdCarrito)
            .all()
        )

        return [
            {
                "IdDetalle": i.IdDetalle,
                "IdProducto": i.IdProducto,
                "Cantidad": i.Cantidad,
                "PrecioUnitario": float(i.PrecioUnitario or 0),
                "Subtotal": float(i.Subtotal or 0)
            }
            for i in items
        ]

    @staticmethod
    def agregar(id_cliente, data):
        carrito = db.session.query(Carrito).filter_by(IdCliente=id_cliente).first()
        if not carrito:
            carrito = Carrito(IdCliente=id_cliente)
            db.session.add(carrito)
            db.session.commit()

        detalle = CarritoDetalle(
            IdCarrito=carrito.IdCarrito,
            IdProducto=data["IdProducto"],
            Cantidad=data.get("Cantidad", 1),
            PrecioUnitario=None  # trigger lo ajusta
        )

        db.session.add(detalle)
        db.session.commit()

        return {"message": "Producto agregado al carrito"}

    @staticmethod
    def actualizar(id_cliente, id_producto, data):
        carrito = db.session.query(Carrito).filter_by(IdCliente=id_cliente).first()
        if not carrito:
            return {"error": "Carrito no encontrado"}

        detalle = (
            db.session.query(CarritoDetalle)
            .filter_by(IdCarrito=carrito.IdCarrito, IdProducto=id_producto)
            .first()
        )

        if not detalle:
            return {"error": "Producto no está en el carrito"}

        detalle.Cantidad = data.get("Cantidad", detalle.Cantidad)
        db.session.commit()

        return {"message": "Cantidad actualizada"}

    @staticmethod
    def eliminar(id_cliente, id_producto):
        carrito = db.session.query(Carrito).filter_by(IdCliente=id_cliente).first()
        if not carrito:
            return {"error": "Carrito no encontrado"}

        detalle = (
            db.session.query(CarritoDetalle)
            .filter_by(IdCarrito=carrito.IdCarrito, IdProducto=id_producto)
            .first()
        )

        if not detalle:
            return {"error": "Producto no está en el carrito"}

        db.session.delete(detalle)
        db.session.commit()

        return {"message": "Producto eliminado del carrito"}
