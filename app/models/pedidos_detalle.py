import decimal
from typing import Optional
from sqlalchemy import Integer, DECIMAL, Computed, ForeignKeyConstraint, Index, PrimaryKeyConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class PedidosDetalle(Base):
    __tablename__ = "PedidosDetalle"
    __table_args__ = (
        ForeignKeyConstraint(
            ["IdPedido"], ["sc_ventas.Pedidos.IdPedido"],
            ondelete="CASCADE", name="FK_PedidosDetalle_Pedidos"
        ),
        ForeignKeyConstraint(
            ["IdProducto"], ["sc_ventas.Productos.IdProducto"],
            ondelete="CASCADE", name="FK_PedidosDetalle_Productos"
        ),
        PrimaryKeyConstraint("IdDetalle", name="PK_PedidosDetalle"),
        Index("IX_PedidosDetalle_IdPedido", "IdPedido"),
        Index("IX_PedidosDetalle_IdProducto", "IdProducto"),
        Index("UQ_PedidosDetalle_Uniq", "IdPedido", "IdProducto", unique=True),
        {"schema": "sc_ventas"},
    )

    IdDetalle: Mapped[int] = mapped_column(Integer, primary_key=True)
    IdPedido: Mapped[int] = mapped_column(Integer, nullable=False)
    IdProducto: Mapped[int] = mapped_column(Integer, nullable=False)
    Cantidad: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("((1))"))
    PrecioUnitario: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(12, 2))
    Subtotal: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(23, 2), Computed("([Cantidad]*[PrecioUnitario])", persisted=True)
    )

    # Relaciones many-to-one (sin delete-orphan aquí)
    Pedidos_: Mapped["Pedidos"] = relationship("Pedidos", back_populates="PedidosDetalle")
    Productos_: Mapped["Productos"] = relationship("Productos", back_populates="PedidosDetalle")