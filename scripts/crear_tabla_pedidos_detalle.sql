-- Script para crear la tabla PedidosDetalle en SQL Server
-- Ejecuta este script en tu base de datos DB_TiendaOnline

USE DB_TiendaOnline;
GO

-- Crear la tabla PedidosDetalle si no existe
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'sc_ventas.PedidosDetalle') AND type in (N'U'))
BEGIN
    CREATE TABLE sc_ventas.PedidosDetalle (
        IdDetalle INT IDENTITY(1,1) PRIMARY KEY,
        IdPedido INT NOT NULL,
        IdProducto INT NOT NULL,
        Cantidad INT NOT NULL DEFAULT 1,
        PrecioUnitario DECIMAL(12,2) NULL,
        Subtotal AS (Cantidad * PrecioUnitario) PERSISTED,
        
        CONSTRAINT FK_PedidosDetalle_Pedidos 
            FOREIGN KEY (IdPedido) 
            REFERENCES sc_ventas.Pedidos(IdPedido) 
            ON DELETE CASCADE,
            
        CONSTRAINT FK_PedidosDetalle_Productos 
            FOREIGN KEY (IdProducto) 
            REFERENCES sc_ventas.Productos(IdProducto) 
            ON DELETE CASCADE,
            
        CONSTRAINT UQ_PedidosDetalle_Uniq 
            UNIQUE (IdPedido, IdProducto)
    );
    
    -- Crear índices
    CREATE INDEX IX_PedidosDetalle_IdPedido ON sc_ventas.PedidosDetalle(IdPedido);
    CREATE INDEX IX_PedidosDetalle_IdProducto ON sc_ventas.PedidosDetalle(IdProducto);
    
    PRINT 'Tabla PedidosDetalle creada exitosamente';
END
ELSE
BEGIN
    PRINT 'La tabla PedidosDetalle ya existe';
END
GO

