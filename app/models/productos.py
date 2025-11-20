import decimal
from typing import Optional
from sqlalchemy import Integer, Unicode, DECIMAL, Boolean, text, Index, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Productos(Base):
    __tablename__ = "Productos"
    __table_args__ = (
        PrimaryKeyConstraint("IdProducto", name="PK_Productos"),
        Index("IX_Productos_Nombre", "Nombre"),
        {"schema": "sc_ventas"},
    )

    IdProducto: Mapped[int] = mapped_column(Integer, primary_key=True)
    Nombre: Mapped[str] = mapped_column(Unicode(150), nullable=False)
    Descripcion: Mapped[Optional[str]] = mapped_column(Unicode(500))
    Precio: Mapped[decimal.Decimal] = mapped_column(DECIMAL(12, 2), nullable=False, server_default=text("((0))"))
    Stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("((0))"))
    Activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("((1))"))

    CarritoDetalle: Mapped[list["CarritoDetalle"]] = relationship("CarritoDetalle", back_populates="Productos_")