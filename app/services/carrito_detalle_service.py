from app.extensions import db
import traceback
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
        detalle = db.session.get(CarritoDetalle, id_detalle)
        if not detalle:
            return {"error": "Detalle no encontrado"}
        return CarritoDetalleService.to_dict(detalle)

    @staticmethod
    def obtener_items(id_carrito):
        """Obtener items de un carrito específico"""
        items = db.session.query(CarritoDetalle).filter_by(IdCarrito=id_carrito).all()
        return [CarritoDetalleService.to_dict(i) for i in items]

 



    @staticmethod
    def agregar(id_carrito, data):
        """
        Agregar o actualizar un producto en el carrito.
        Siempre se usa el último carrito creado para el cliente,
        aunque esté vacío, hasta que se finalice la compra.
        """
        # 1. Buscar producto
        try:
            producto = db.session.get(Productos, data["IdProducto"])
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[CarritoDetalleService] Error al buscar producto: {str(e)}\n{tb}")
            return {"error": f"Error al buscar producto: {str(e)}", "trace": tb}

        if not producto or not producto.Activo:
            return {"error": "Producto no disponible"}

        # 2. Buscar el último carrito del cliente
        # 2. Buscar carrito anónimo (IdCliente NULL)
        carrito = (
            db.session.query(Carrito)
            .filter(Carrito.IdCliente == None)
            .order_by(Carrito.IdCarrito.desc())
            .first()
        )

        # Si no existe, crear uno
        if not carrito:
            carrito = Carrito(IdCliente=None)
            db.session.add(carrito)
            db.session.commit()
            print(f"[CarritoDetalleService] Carrito anónimo creado: IdCarrito={carrito.IdCarrito}")

        id_carrito = carrito.IdCarrito


        # 3. Buscar detalle existente
        detalle_existente = db.session.query(CarritoDetalle).filter_by(
            IdCarrito=id_carrito,
            IdProducto=data["IdProducto"]
        ).first()

        try:
            cantidad = int(data.get("Cantidad", 1))
        except Exception:
            cantidad = 1

        # 4. Actualizar o insertar
        if detalle_existente:
            detalle_existente.Cantidad += cantidad
            try:
                db.session.commit()
                return {"message": "Producto actualizado", "IdCarrito": id_carrito}
            except Exception as e:
                db.session.rollback()
                tb = traceback.format_exc()
                print(f"[CarritoDetalleService] Error al actualizar detalle: {str(e)}\n{tb}")
                return {"error": f"Error al actualizar detalle: {str(e)}", "trace": tb}
        else:
            detalle = CarritoDetalle(
                IdCarrito=id_carrito,
                IdProducto=data["IdProducto"],
                Cantidad=cantidad,
                PrecioUnitario=producto.Precio
            )
            db.session.add(detalle)
            try:
                db.session.commit()
                return {"message": "Producto agregado", "IdCarrito": id_carrito}
            except Exception as e:
                db.session.rollback()
                tb = traceback.format_exc()
                print(f"[CarritoDetalleService] Error al guardar detalle: {str(e)}\n{tb}")
                return {"error": f"Error al guardar detalle: {str(e)}", "trace": tb}
        
    @staticmethod
    def obtener_productos_disponibles():
        """
        Retorna todos los productos activos/disponibles.
        """
        try:
            productos = db.session.query(Productos).filter_by(Activo=True).all()
            return productos
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[CarritoDetalleService] Error al obtener productos: {str(e)}\n{tb}")
            return []


    @staticmethod
    def actualizar(id_cliente, id_producto, data):
        """Actualizar la cantidad de un producto en el carrito"""
        try:
            carrito = db.session.query(Carrito).filter_by(IdCliente=id_cliente).first()
            if not carrito:
                return {"error": "Carrito no encontrado"}

            detalle = db.session.query(CarritoDetalle).filter_by(
                IdCarrito=carrito.IdCarrito,
                IdProducto=id_producto
            ).first()

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
    def actualizar_por_detalle(id_detalle, data):
        """Actualizar un detalle por su IdDetalle"""
        try:
            print(f"[CarritoDetalleService] actualizar_por_detalle id_detalle={id_detalle} data={data}")
            detalle = db.session.get(CarritoDetalle, id_detalle)
            if not detalle:
                return {"error": "Detalle no encontrado"}
            # Manejar actualización de producto (IdProducto)
            if "IdProducto" in data:
                try:
                    nuevo_id_producto = int(data.get("IdProducto"))
                except Exception:
                    return {"error": "IdProducto inválido"}
                # Si es diferente, realizar validaciones
                if nuevo_id_producto != detalle.IdProducto:
                    # verificar existencia del producto y que esté activo
                    nuevo_producto = db.session.get(Productos, nuevo_id_producto)
                    if not nuevo_producto or not nuevo_producto.Activo:
                        return {"error": "Producto no disponible"}

                    # Buscar si ya hay un detalle en el mismo carrito con el producto destino
                    detalle_existente_destino = db.session.query(CarritoDetalle).filter_by(
                        IdCarrito=detalle.IdCarrito,
                        IdProducto=nuevo_id_producto
                    ).first()

                    # Determinar la cantidad entrante (si se pasó, usarla; si no, usar la actual del detalle)
                    try:
                        cantidad_nueva = int(data.get("Cantidad", detalle.Cantidad))
                    except Exception:
                        cantidad_nueva = detalle.Cantidad

                    if detalle_existente_destino and detalle_existente_destino.IdDetalle != detalle.IdDetalle:
                        # Hacer merge: sumar cantidades y actualizar precio unitario al del nuevo producto
                        detalle_existente_destino.Cantidad = int((detalle_existente_destino.Cantidad or 0) + cantidad_nueva)
                        detalle_existente_destino.PrecioUnitario = nuevo_producto.Precio
                        # eliminar el detalle original
                        db.session.delete(detalle)
                        db.session.commit()
                        # devolver el detalle destino actualizado
                        return CarritoDetalleService.to_dict(detalle_existente_destino)
                    else:
                        # No existe detalle destino, actualizar IdProducto del detalle actual
                        detalle.IdProducto = nuevo_id_producto
                        # actualizar precio unitario
                        detalle.PrecioUnitario = nuevo_producto.Precio
                        # ajustar la cantidad si se brindó
                        if "Cantidad" in data:
                            if int(data.get("Cantidad")) <= 0:
                                return {"error": "La cantidad debe ser mayor a 0"}
                            detalle.Cantidad = int(data.get("Cantidad"))
            if "Cantidad" in data:
                if int(data["Cantidad"]) <= 0:
                    return {"error": "La cantidad debe ser mayor a 0"}
                detalle.Cantidad = int(data["Cantidad"])  # convertir por si viene como string

            if "PrecioUnitario" in data:
                detalle.PrecioUnitario = data["PrecioUnitario"]

            db.session.commit()
            detalle_guardado = db.session.get(CarritoDetalle, id_detalle)
            print(f"[CarritoDetalleService] detalle actualizado id_detalle={id_detalle} Cantidad={detalle_guardado.Cantidad} IdProducto={detalle_guardado.IdProducto}")
            return CarritoDetalleService.to_dict(detalle_guardado)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar detalle por id: {str(e)}"}

    @staticmethod
    def eliminar(id_cliente, id_producto):
        """Eliminar un producto del carrito"""
        try:
            carrito = db.session.query(Carrito).filter_by(IdCliente=id_cliente).first()
            if not carrito:
                return {"error": "Carrito no encontrado"}

            detalle = db.session.query(CarritoDetalle).filter_by(
                IdCarrito=carrito.IdCarrito,
                IdProducto=id_producto
            ).first()

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
            detalle = db.session.get(CarritoDetalle, id_detalle)
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
            carrito = db.session.query(Carrito).filter_by(IdCliente=id_cliente).first()
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
    def limpiar_carrito_por_idcarrito(id_carrito):
        """Eliminar todos los productos del carrito por IdCarrito"""
        try:
            detalles = db.session.query(CarritoDetalle).filter(
                CarritoDetalle.IdCarrito == id_carrito
            ).all()

            if not detalles:
                return {"message": "Carrito ya vacío o no existe"}

            for detalle in detalles:
                db.session.delete(detalle)
            db.session.commit()
            return {"message": "Carrito limpiado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al limpiar carrito por id: {str(e)}"}

    @staticmethod
    def obtener_total_carrito(id_cliente):
        """Calcular el total del carrito de un cliente"""
        items = CarritoDetalleService.obtener_items(id_cliente)
        total = sum((i["Cantidad"] * i["PrecioUnitario"]) for i in items)
        cantidad_total = sum(i["Cantidad"] for i in items)
        return {"Total": total, "Items": len(items), "CantidadTotal": cantidad_total}

    @staticmethod
    def to_dict(d):
        """Convertir modelo a diccionario"""
        return {
            "IdDetalle": d.IdDetalle,
            "IdCarrito": d.IdCarrito,
            "IdProducto": d.IdProducto,
            "Cantidad": d.Cantidad,
            "PrecioUnitario": float(d.PrecioUnitario or 0),
            "Subtotal": float((d.Cantidad or 0) * (d.PrecioUnitario or 0)),
            # datos del producto para UI
            "NombreProducto": getattr(d.Productos_, "Nombre", None),
            "Stock": getattr(d.Productos_, "Stock", None)
        }



    # duplicate implementation removed above

    @staticmethod
    def eliminar(id_cliente, id_producto):
        """Eliminar un producto del carrito"""
        try:
            carrito = db.session.query(Carrito).filter_by(IdCliente=id_cliente).first()
            if not carrito:
                return {"error": "Carrito no encontrado"}

            detalle = db.session.query(CarritoDetalle).filter_by(
                IdCarrito=carrito.IdCarrito,
                IdProducto=id_producto
            ).first()

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
            detalle = db.session.get(CarritoDetalle, id_detalle)
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
            carrito = db.session.query(Carrito).filter_by(IdCliente=id_cliente).first()
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
    def limpiar_carrito_por_idcarrito(id_carrito):
        """Eliminar todos los productos del carrito por IdCarrito"""
        try:
            detalles = db.session.query(CarritoDetalle).filter(
                CarritoDetalle.IdCarrito == id_carrito
            ).all()

            if not detalles:
                return {"message": "Carrito ya vacío o no existe"}

            for detalle in detalles:
                db.session.delete(detalle)
            db.session.commit()
            return {"message": "Carrito limpiado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al limpiar carrito por id: {str(e)}"}

    @staticmethod
    def obtener_total_carrito(id_cliente):
        """Calcular el total del carrito de un cliente"""
        items = CarritoDetalleService.obtener_items(id_cliente)
        total = sum((i["Cantidad"] * i["PrecioUnitario"]) for i in items)
        cantidad_total = sum(i["Cantidad"] for i in items)
        return {"Total": total, "Items": len(items), "CantidadTotal": cantidad_total}

    @staticmethod
    def to_dict(d):
        """Convertir modelo a diccionario"""
        return {
            "IdDetalle": d.IdDetalle,
            "IdCarrito": d.IdCarrito,
            "IdProducto": d.IdProducto,
            "Cantidad": d.Cantidad,
            "PrecioUnitario": float(d.PrecioUnitario or 0),
            "Subtotal": float((d.Cantidad or 0) * (d.PrecioUnitario or 0)),
            # datos del producto para UI
            "NombreProducto": getattr(d.Productos_, "Nombre", None),
            "Stock": getattr(d.Productos_, "Stock", None)
        }

    @staticmethod
    def obtener_productos_disponibles():
        """Obtener productos activos y con stock"""
        try:
            productos = db.session.query(Productos).filter(Productos.Activo == True).all()
            return [
                {
                    "IdProducto": p.IdProducto,
                    "Nombre": p.Nombre,
                    "Precio": float(p.Precio),
                    "Stock": p.Stock
                }
                for p in productos
            ]
        except Exception as e:
            return {"error": f"Error al obtener productos: {str(e)}"}