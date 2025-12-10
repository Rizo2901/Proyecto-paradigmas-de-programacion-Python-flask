import datetime
import decimal
from typing import Optional
from sqlalchemy import Integer, Unicode, DECIMAL, DateTime, ForeignKeyConstraint, Index, PrimaryKeyConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Pedidos(Base):
    __tablename__ = "Pedidos"
    __table_args__ = (
        ForeignKeyConstraint(["IdCliente"], ["sc_ventas.Clientes.IdCliente"], onupdate="CASCADE", name="FK_Pedidos_Clientes"),
        PrimaryKeyConstraint("IdPedido", name="PK_Pedidos"),
        Index("IX_Pedidos_Estado", "Estado"),
        Index("IX_Pedidos_IdCliente", "IdCliente"),
        {"schema": "sc_ventas"},
    )

    IdPedido: Mapped[int] = mapped_column(Integer, primary_key=True)
    IdCliente: Mapped[int] = mapped_column(Integer, nullable=False)
    FechaPedido: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("(SYSUTCDATETIME())"))
    Total: Mapped[decimal.Decimal] = mapped_column(DECIMAL(12, 2), nullable=False, server_default=text("((0))"))
    Estado: Mapped[str] = mapped_column(Unicode(20), nullable=False, server_default=text("(N'Pendiente')"))
    Notas: Mapped[Optional[str]] = mapped_column(Unicode(500), nullable=True)
    TiendaEnvio: Mapped[Optional[str]] = mapped_column(Unicode(200), nullable=True)

    Clientes_: Mapped["Clientes"] = relationship("Clientes", back_populates="Pedidos")
    PedidosDetalle: Mapped[list["PedidosDetalle"]] = relationship("PedidosDetalle", back_populates="Pedidos_", cascade="all, delete-orphan")