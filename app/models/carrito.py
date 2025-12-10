import datetime
from sqlalchemy import Integer, DateTime, ForeignKeyConstraint, Index, PrimaryKeyConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Carrito(Base):
    __tablename__ = "Carrito"
    __table_args__ = (
        ForeignKeyConstraint(["IdCliente"], ["sc_ventas.Clientes.IdCliente"], ondelete="CASCADE", onupdate="CASCADE", name="FK_Carrito_Clientes"),
        PrimaryKeyConstraint("IdCarrito", name="PK_Carrito"),
        Index("IX_Carrito_IdCliente", "IdCliente"),
        {"schema": "sc_ventas"},
    )

    IdCarrito: Mapped[int] = mapped_column(Integer, primary_key=True)
    IdCliente: Mapped[int] = mapped_column(Integer, nullable=False)
    FechaCreacion: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text("(SYSUTCDATETIME())"))

    Clientes_: Mapped["Clientes"] = relationship("Clientes", back_populates="Carrito")
    CarritoDetalle: Mapped[list["CarritoDetalle"]] = relationship("CarritoDetalle", back_populates="Carrito_")