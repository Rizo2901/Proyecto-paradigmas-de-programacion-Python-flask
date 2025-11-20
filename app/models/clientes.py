import datetime
from typing import Optional
from sqlalchemy import Integer, Unicode, DATETIME2, text, Index, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Clientes(Base):
    __tablename__ = "Clientes"
    __table_args__ = (
        PrimaryKeyConstraint("IdCliente", name="PK_Clientes"),
        Index("UQ_Clientes_Correo", "Correo", unique=True),
        {"schema": "sc_ventas"},
    )

    IdCliente: Mapped[int] = mapped_column(Integer, primary_key=True)
    Nombre: Mapped[str] = mapped_column(Unicode(120), nullable=False)
    Correo: Mapped[str] = mapped_column(Unicode(256), nullable=False)
    Telefono: Mapped[Optional[str]] = mapped_column(Unicode(25))
    Direccion: Mapped[Optional[str]] = mapped_column(Unicode(300))
    FechaRegistro: Mapped[datetime.datetime] = mapped_column(DATETIME2, nullable=False, server_default=text("(SYSUTCDATETIME())"))

    Carrito: Mapped[list["Carrito"]] = relationship("Carrito", back_populates="Clientes_")
    Pedidos: Mapped[list["Pedidos"]] = relationship("Pedidos", back_populates="Clientes_")