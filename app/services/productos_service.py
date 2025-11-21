from extensions import db
from models.productos import Productos
from sqlalchemy import text

class ProductosService:

    @staticmethod
    def obtener_todos():
        sp = text("EXEC sc_ventas.SP_ObtenerProductos")
        result = db.session.execute(sp).mappings().all()
        return [dict(row) for row in result]

    @staticmethod
    def obtener_por_id(id_producto):
        producto = db.session.query(Productos).get(id_producto)
        if not producto:
            return {"error": "Producto no encontrado"}
        return ProductosService.to_dict(producto)

    @staticmethod
    def crear(data):
        sp = text("""
            EXEC sc_ventas.SP_InsertarProducto 
                :Nombre, :Descripcion, :Precio, :Stock
        """)

        db.session.execute(sp, {
            "Nombre": data["Nombre"],
            "Descripcion": data.get("Descripcion"),
            "Precio": data["Precio"],
            "Stock": data["Stock"]
        })
        db.session.commit()

        return {"message": "Producto creado correctamente"}

    @staticmethod
    def actualizar(id_producto, data):
        producto = db.session.query(Productos).get(id_producto)
        if not producto:
            return {"error": "Producto no encontrado"}

        producto.Nombre = data.get("Nombre", producto.Nombre)
        producto.Descripcion = data.get("Descripcion", producto.Descripcion)
        producto.Precio = data.get("Precio", producto.Precio)
        producto.Stock = data.get("Stock", producto.Stock)
        producto.Activo = data.get("Activo", producto.Activo)

        db.session.commit()

        return ProductosService.to_dict(producto)

    @staticmethod
    def eliminar(id_producto):
        producto = db.session.query(Productos).get(id_producto)
        if not producto:
            return {"error": "Producto no encontrado"}

        db.session.delete(producto)
        db.session.commit()

        return {"message": "Producto eliminado correctamente"}

    @staticmethod
    def to_dict(p):
        return {
            "IdProducto": p.IdProducto,
            "Nombre": p.Nombre,
            "Descripcion": p.Descripcion,
            "Precio": float(p.Precio),
            "Stock": p.Stock,
            "Activo": p.Activo
        }
