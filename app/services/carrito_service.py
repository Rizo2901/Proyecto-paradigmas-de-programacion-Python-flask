from app.extensions import db
from app.models.carrito import Carrito
from app.models.carrito_detalle import CarritoDetalle

class CarritoService:

    @staticmethod
    def obtener_todos():
        carritos = db.session.query(Carrito).all()
        return [CarritoService.to_dict(c) for c in carritos]

    @staticmethod
    def obtener_carrito(id_cliente):
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
        carrito = db.session.query(Carrito).get(id_carrito)
        if not carrito:
            return {"error": "Carrito no encontrado"}
        return CarritoService.to_dict(carrito)

    @staticmethod
    def crear_carrito(id_cliente):
        try:
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

        # Obtener nombre del producto para cada detalle de forma segura
        from app.models.productos import Productos
        detalles_with_name = []
        for d in detalles:
            nombre_producto = ""
            try:
                prod = db.session.query(Productos).filter(Productos.IdProducto == d.IdProducto).first()
                if prod and hasattr(prod, "Nombre"):
                    nombre_producto = prod.Nombre
            except Exception:
                nombre_producto = ""
            detalles_with_name.append({
                "IdDetalle": d.IdDetalle,
                "IdProducto": d.IdProducto,
                "Cantidad": d.Cantidad,
                "PrecioUnitario": float(d.PrecioUnitario or 0),
                "Subtotal": float(d.Subtotal or 0),
                "NombreProducto": nombre_producto
            })

        return {
            **CarritoService.to_dict(carrito),
            "Detalles": detalles_with_name
        }

    @staticmethod
    def obtener_productos_disponibles():
        from app.models.productos import Productos
        return [
            {
                "IdProducto": p.IdProducto,
                "Nombre": p.Nombre,
                "Precio": float(p.Precio),
                "Stock": p.Stock
            }
            for p in db.session.query(Productos).filter(Productos.Activo == True, Productos.Stock > 0).all()
        ]

    @staticmethod
    def agregar_producto(id_cliente, id_producto):
        """Agregar un producto al carrito del cliente"""
        from app.models.productos import Productos
        carrito = (
            db.session.query(Carrito)
            .filter(Carrito.IdCliente == id_cliente)
            .first()
        )

        if not carrito:
            carrito = Carrito(IdCliente=id_cliente)
            db.session.add(carrito)
            db.session.commit()

        id_carrito = carrito.IdCarrito

        producto = db.session.query(Productos).get(id_producto)
        if not producto:
            return {"error": "Producto no encontrado"}
        precio = float(producto.Precio)

        detalle = (
            db.session.query(CarritoDetalle)
            .filter(
                CarritoDetalle.IdCarrito == id_carrito,
                CarritoDetalle.IdProducto == id_producto
            )
            .first()
        )

        if detalle:
            detalle.Cantidad += 1
            detalle.PrecioUnitario = precio
        else:
            detalle = CarritoDetalle(
                IdCarrito=id_carrito,
                IdProducto=id_producto,
                Cantidad=1,
                PrecioUnitario=precio,
            )
            db.session.add(detalle)

        try:
            db.session.commit()
            return {
                "message": f"Producto {id_producto} agregado al carrito",
                "IdCarrito": id_carrito
            }
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}

    @staticmethod
    def to_dict(c):
        return {
            "IdCarrito": c.IdCarrito,
            "IdCliente": c.IdCliente,
            "FechaCreacion": str(c.FechaCreacion)
        }
