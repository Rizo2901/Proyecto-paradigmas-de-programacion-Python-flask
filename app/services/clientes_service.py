from extensions import db
from models.clientes import Clientes
from sqlalchemy import text

class ClientesService:

    @staticmethod
    def obtener_todos():
        clientes = db.session.query(Clientes).all()
        return [ClientesService.to_dict(c) for c in clientes]

    @staticmethod
    def obtener_por_id(id_cliente):
        cliente = db.session.query(Clientes).get(id_cliente)
        if not cliente:
            return {"error": "Cliente no encontrado"}
        return ClientesService.to_dict(cliente)

    @staticmethod
    def crear(data):
        nombre = data.get("Nombre")
        correo = data.get("Correo")
        telefono = data.get("Telefono")
        direccion = data.get("Direccion")

        sp = text("""
            EXEC sc_ventas.SP_InsertarCliente 
                :Nombre, :Correo, :Telefono, :Direccion
        """)

        db.session.execute(sp, {
            "Nombre": nombre,
            "Correo": correo,
            "Telefono": telefono,
            "Direccion": direccion
        })
        db.session.commit()

        return {"message": "Cliente creado correctamente"}

    @staticmethod
    def actualizar(id_cliente, data):
        cliente = db.session.query(Clientes).get(id_cliente)
        if not cliente:
            return {"error": "Cliente no encontrado"}

        cliente.Nombre = data.get("Nombre", cliente.Nombre)
        cliente.Correo = data.get("Correo", cliente.Correo)
        cliente.Telefono = data.get("Telefono", cliente.Telefono)
        cliente.Direccion = data.get("Direccion", cliente.Direccion)

        db.session.commit()

        return ClientesService.to_dict(cliente)

    @staticmethod
    def eliminar(id_cliente):
        cliente = db.session.query(Clientes).get(id_cliente)
        if not cliente:
            return {"error": "Cliente no encontrado"}

        db.session.delete(cliente)
        db.session.commit()

        return {"message": "Cliente eliminado correctamente"}

    @staticmethod
    def to_dict(c):
        return {
            "IdCliente": c.IdCliente,
            "Nombre": c.Nombre,
            "Correo": c.Correo,
            "Telefono": c.Telefono,
            "Direccion": c.Direccion,
            "FechaRegistro": str(c.FechaRegistro)
        }
