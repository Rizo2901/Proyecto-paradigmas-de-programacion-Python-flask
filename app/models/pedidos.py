import datetime
import decimal
from sqlalchemy import Integer, Unicode, DECIMAL, DATETIME2, ForeignKeyConstraint, Index, PrimaryKeyConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

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
    FechaPedido: Mapped[datetime.datetime] = mapped_column(DATETIME2, nullable=False, server_default=text("(SYSUTCDATETIME())"))
    Total: Mapped[decimal.Decimal] = mapped_column(DECIMAL(12, 2), nullable=False, server_default=text("((0))"))
    Estado: Mapped[str] = mapped_column(Unicode(20), nullable=False, server_default=text("(N'Pendiente')"))

    Clientes_: Mapped["Clientes"] = relationship("Clientes", back_populates="Pedidos")