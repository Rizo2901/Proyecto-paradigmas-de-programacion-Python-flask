-- Script para agregar la columna TiendaEnvio a la tabla Pedidos
USE DB_TiendaOnline;
GO

-- Verificar si la columna ya existe antes de agregarla
IF NOT EXISTS (
    SELECT 1 FROM sys.columns 
    WHERE object_id = OBJECT_ID('sc_ventas.Pedidos') 
    AND name = 'TiendaEnvio'
)
BEGIN
    ALTER TABLE sc_ventas.Pedidos
    ADD TiendaEnvio NVARCHAR(200) NULL;
    
    PRINT 'Columna TiendaEnvio agregada exitosamente a la tabla Pedidos.';
END
ELSE
BEGIN
    PRINT 'La columna TiendaEnvio ya existe en la tabla Pedidos.';
END
GO

