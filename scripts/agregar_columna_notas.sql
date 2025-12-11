-- Script para agregar la columna Notas a la tabla Pedidos
USE DB_TiendaOnline;
GO

-- Verificar si la columna ya existe antes de agregarla
IF NOT EXISTS (
    SELECT 1 FROM sys.columns 
    WHERE object_id = OBJECT_ID('sc_ventas.Pedidos') 
    AND name = 'Notas'
)
BEGIN
    ALTER TABLE sc_ventas.Pedidos
    ADD Notas NVARCHAR(500) NULL;
    
    PRINT 'Columna Notas agregada exitosamente a la tabla Pedidos.';
END
ELSE
BEGIN
    PRINT 'La columna Notas ya existe en la tabla Pedidos.';
END
GO

