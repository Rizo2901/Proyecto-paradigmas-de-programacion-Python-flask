from app.extensions import db
from app.models.carrito_detalle import CarritoDetalle
from app.models.carrito import Carrito
from app.models.productos import Productos

class CarritoDetalleService:

    @staticmethod
    def obtener_todos():
        """Obtener todos los detalles de carrito"""
        detalles = db.session.query(CarritoDetalle).all()
        return [CarritoDetalleService.to_dict(d) for d in detalles]

    @staticmethod
    def obtener_por_id(id_detalle):
        """Obtener un detalle por su ID"""
        detalle = db.session.query(CarritoDetalle).get(id_detalle)
        if not detalle:
            return {"error": "Detalle no encontrado"}
        return CarritoDetalleService.to_dict(detalle)

    @staticmethod
    def obtener_items(id_cliente):
        """Obtener items del carrito de un cliente"""
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

        return [CarritoDetalleService.to_dict(i) for i in items]

    @staticmethod
    def agregar(id_cliente, data):
        """Agregar un producto al carrito"""
        try:
            # Obtener o crear carrito
            carrito = db.session.query(Carrito).filter_by(
                IdCliente=id_cliente
            ).first()

            if not carrito:
                carrito = Carrito(IdCliente=id_cliente)
                db.session.add(carrito)
                db.session.flush()  # Para obtener el ID

            # Verificar que el producto existe
            producto = db.session.query(Productos).get(data["IdProducto"])
            if not producto:
                return {"error": "Producto no encontrado"}

            if not producto.Activo:
                return {"error": "Producto no está disponible"}

            # Verificar si el producto ya está en el carrito
            detalle_existente = db.session.query(CarritoDetalle).filter_by(
                IdCarrito=carrito.IdCarrito,
                IdProducto=data["IdProducto"]
            ).first()

            cantidad = data.get("Cantidad", 1)

            if detalle_existente:
                # Actualizar cantidad si ya existe
                detalle_existente.Cantidad += cantidad
                detalle_existente.PrecioUnitario = producto.Precio
            else:
                # Crear nuevo detalle
                detalle = CarritoDetalle(
                    IdCarrito=carrito.IdCarrito,
                    IdProducto=data["IdProducto"],
                    Cantidad=cantidad,
                    PrecioUnitario=producto.Precio
                )
                db.session.add(detalle)

            db.session.commit()
            return {"message": "Producto agregado al carrito"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al agregar producto: {str(e)}"}

    @staticmethod
    def actualizar(id_cliente, id_producto, data):
        """Actualizar la cantidad de un producto en el carrito"""
        try:
            carrito = db.session.query(Carrito).filter_by(
                IdCliente=id_cliente
            ).first()

            if not carrito:
                return {"error": "Carrito no encontrado"}

            detalle = (
                db.session.query(CarritoDetalle)
                .filter_by(
                    IdCarrito=carrito.IdCarrito,
                    IdProducto=id_producto
                )
                .first()
            )

            if not detalle:
                return {"error": "Producto no está en el carrito"}

            if "Cantidad" in data:
                if data["Cantidad"] <= 0:
                    return {"error": "La cantidad debe ser mayor a 0"}
                detalle.Cantidad = data["Cantidad"]

            if "PrecioUnitario" in data:
                detalle.PrecioUnitario = data["PrecioUnitario"]

            db.session.commit()
            return CarritoDetalleService.to_dict(detalle)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar detalle: {str(e)}"}

    @staticmethod
    def eliminar(id_cliente, id_producto):
        """Eliminar un producto del carrito"""
        try:
            carrito = db.session.query(Carrito).filter_by(
                IdCliente=id_cliente
            ).first()

            if not carrito:
                return {"error": "Carrito no encontrado"}

            detalle = (
                db.session.query(CarritoDetalle)
                .filter_by(
                    IdCarrito=carrito.IdCarrito,
                    IdProducto=id_producto
                )
                .first()
            )

            if not detalle:
                return {"error": "Producto no está en el carrito"}

            db.session.delete(detalle)
            db.session.commit()
            return {"message": "Producto eliminado del carrito"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al eliminar producto: {str(e)}"}

    @staticmethod
    def eliminar_por_id(id_detalle):
        """Eliminar un detalle por su ID"""
        try:
            detalle = db.session.query(CarritoDetalle).get(id_detalle)
            if not detalle:
                return {"error": "Detalle no encontrado"}

            db.session.delete(detalle)
            db.session.commit()
            return {"message": "Detalle eliminado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al eliminar detalle: {str(e)}"}

    @staticmethod
    def limpiar_carrito(id_cliente):
        """Eliminar todos los productos del carrito de un cliente"""
        try:
            carrito = db.session.query(Carrito).filter_by(
                IdCliente=id_cliente
            ).first()

            if not carrito:
                return {"error": "Carrito no encontrado"}

            detalles = db.session.query(CarritoDetalle).filter(
                CarritoDetalle.IdCarrito == carrito.IdCarrito
            ).all()

            for detalle in detalles:
                db.session.delete(detalle)

            db.session.commit()
            return {"message": "Carrito limpiado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al limpiar carrito: {str(e)}"}

    @staticmethod
    def obtener_total_carrito(id_cliente):
        """Calcular el total del carrito de un cliente"""
        items = CarritoDetalleService.obtener_items(id_cliente)
        total = sum(item.get("Subtotal", 0) for item in items)
        return {"Total": total, "Items": len(items)}

    @staticmethod
    def to_dict(d):
        """Convertir modelo a diccionario"""
        return {
            "IdDetalle": d.IdDetalle,
            "IdCarrito": d.IdCarrito,
            "IdProducto": d.IdProducto,
            "Cantidad": d.Cantidad,
            "PrecioUnitario": float(d.PrecioUnitario or 0),
            "Subtotal": float(d.Subtotal or 0)
        }
