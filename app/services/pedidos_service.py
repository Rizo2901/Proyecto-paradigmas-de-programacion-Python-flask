from extensions import db
from models.pedidos import Pedidos
from sqlalchemy import text

class PedidosService:

    @staticmethod
    def crear_pedido(id_cliente):
        sp = text("EXEC sc_ventas.SP_CrearPedido :IdCliente")

        try:
            db.session.execute(sp, {"IdCliente": id_cliente})
            db.session.commit()
        except Exception as e:
            return {"error": str(e)}

        return {"message": "Pedido creado correctamente"}

    @staticmethod
    def obtener_pedidos(id_cliente):
        pedidos = (
            db.session.query(Pedidos)
            .filter(Pedidos.IdCliente == id_cliente)
            .all()
        )

        return [PedidosService.to_dict(p) for p in pedidos]

    @staticmethod
    def obtener_por_id(id_pedido):
        pedido = db.session.query(Pedidos).get(id_pedido)
        if not pedido:
            return {"error": "Pedido no encontrado"}
        return PedidosService.to_dict(pedido)

    @staticmethod
    def to_dict(p):
        return {
            "IdPedido": p.IdPedido,
            "IdCliente": p.IdCliente,
            "FechaPedido": str(p.FechaPedido),
            "Total": float(p.Total),
            "Estado": p.Estado
        }
