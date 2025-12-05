from app.extensions import db
from app.models.productos import Productos
from app.models.carrito_detalle import CarritoDetalle
from app.models.pedidos_detalle import PedidosDetalle
class ProductosService:

    @staticmethod
    def obtener_todos():
        """Obtener todos los productos"""
        productos = db.session.query(Productos).all()
        return [ProductosService.to_dict(p) for p in productos]

    @staticmethod
    def obtener_activos():
        """Obtener solo productos activos"""
        productos = db.session.query(Productos).filter(Productos.Activo == True).all()
        return [ProductosService.to_dict(p) for p in productos]

    @staticmethod
    def obtener_por_id(id_producto):
        """Obtener un producto por su ID"""
        producto = db.session.query(Productos).get(id_producto)
        if not producto:
            return {"error": "Producto no encontrado"}
        return ProductosService.to_dict(producto)

    @staticmethod
    def crear(data):
        """Crear un nuevo producto"""
        try:
            producto = Productos(
                Nombre=data.get("Nombre"),
                Descripcion=data.get("Descripcion"),
                Precio=data.get("Precio", 0),
                Stock=data.get("Stock", 0),
                Activo=data.get("Activo", True)
            )
            db.session.add(producto)
            db.session.commit()
            return ProductosService.to_dict(producto)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al crear producto: {str(e)}"}

    @staticmethod
    def actualizar(id_producto, data):
        """Actualizar un producto existente"""
        try:
            producto = db.session.query(Productos).get(id_producto)
            if not producto:
                return {"error": "Producto no encontrado"}

            if "Nombre" in data:
                producto.Nombre = data["Nombre"]
            if "Descripcion" in data:
                producto.Descripcion = data.get("Descripcion")
            if "Precio" in data:
                producto.Precio = data["Precio"]
            if "Stock" in data:
                producto.Stock = data["Stock"]
            if "Activo" in data:
                producto.Activo = data["Activo"]

            db.session.commit()
            return ProductosService.to_dict(producto)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar producto: {str(e)}"}

    @staticmethod
    def eliminar(id_producto):
        """Eliminar un producto (soft delete - desactivar)"""
        try:
            producto = db.session.query(Productos).get(id_producto)
            if not producto:
                return {"error": "Producto no encontrado"}

            producto.Activo = False
            db.session.commit()
            return {"message": "Producto desactivado correctamente"}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al desactivar producto: {str(e)}"}


#Metodo editado arreglos
    @staticmethod
    def eliminar_fisico(id_producto):
        """Eliminar físicamente un producto de la BD
        
        Primero elimina los registros relacionados en CarritoDetalle y PedidosDetalle
        para evitar errores de integridad referencial.
        """
        try:
            producto = db.session.query(Productos).get(id_producto)
            if not producto:
                return {"error": "Producto no encontrado"}

            # Primero eliminar los registros relacionados en CarritoDetalle
            detalles_carrito = db.session.query(CarritoDetalle).filter(
                CarritoDetalle.IdProducto == id_producto
            ).all()
            for detalle in detalles_carrito:
                db.session.delete(detalle)

            # Luego eliminar los registros relacionados en PedidosDetalle
            detalles_pedido = db.session.query(PedidosDetalle).filter(
                PedidosDetalle.IdProducto == id_producto
            ).all()
            for detalle in detalles_pedido:
                db.session.delete(detalle)

            # Finalmente eliminar el producto
            db.session.delete(producto)
            db.session.commit()
            return {"message": "Producto eliminado correctamente"}
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            return {"error": f"Error al eliminar producto: {error_msg}"}
#hasta acá
    @staticmethod
    def buscar_por_nombre(nombre):
        """Buscar productos por nombre (búsqueda parcial)"""
        productos = db.session.query(Productos).filter(
            Productos.Nombre.like(f"%{nombre}%")
        ).all()
        return [ProductosService.to_dict(p) for p in productos]

    @staticmethod
    def actualizar_stock(id_producto, cantidad):
        """Actualizar el stock de un producto"""
        try:
            producto = db.session.query(Productos).get(id_producto)
            if not producto:
                return {"error": "Producto no encontrado"}

            producto.Stock += cantidad
            if producto.Stock < 0:
                return {"error": "Stock insuficiente"}

            db.session.commit()
            return ProductosService.to_dict(producto)
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error al actualizar stock: {str(e)}"}

    @staticmethod
    def to_dict(p):
        """Convertir modelo a diccionario"""
        return {
            "IdProducto": p.IdProducto,
            "Nombre": p.Nombre,
            "Descripcion": p.Descripcion,
            "Precio": float(p.Precio),
            "Stock": p.Stock,
            "Activo": p.Activo
        }
