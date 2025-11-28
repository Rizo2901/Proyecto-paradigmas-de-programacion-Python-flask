import decimal
from typing import Optional
from sqlalchemy import Integer, DECIMAL, Computed, ForeignKeyConstraint, Index, PrimaryKeyConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class CarritoDetalle(Base):
    __tablename__ = "CarritoDetalle"
    __table_args__ = (
        ForeignKeyConstraint(["IdCarrito"], ["sc_ventas.Carrito.IdCarrito"], ondelete="CASCADE", name="FK_CarritoDetalle_Carrito"),
        ForeignKeyConstraint(["IdProducto"], ["sc_ventas.Productos.IdProducto"], onupdate="CASCADE", name="FK_CarritoDetalle_Productos"),
        PrimaryKeyConstraint("IdDetalle", name="PK_CarritoDetalle"),
        Index("IX_CarritoDetalle_IdCarrito", "IdCarrito"),
        Index("IX_CarritoDetalle_IdProducto", "IdProducto"),
        Index("UQ_CarritoDetalle_Uniq", "IdCarrito", "IdProducto", unique=True),

        {"schema": "sc_ventas", "implicit_returning": False},
    )

    IdDetalle: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    IdCarrito: Mapped[int] = mapped_column(Integer, nullable=False)
    IdProducto: Mapped[int] = mapped_column(Integer, nullable=False)
    Cantidad: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("((1))"))
    PrecioUnitario: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(12, 2))

    Subtotal: Mapped[Optional[decimal.Decimal]] = mapped_column(
        DECIMAL(23, 2),
        Computed("([Cantidad]*[PrecioUnitario])", persisted=True)
    )

    Carrito_: Mapped["Carrito"] = relationship("Carrito", back_populates="CarritoDetalle")
    Productos_: Mapped["Productos"] = relationship("Productos", back_populates="CarritoDetalle")
