-- Script para agregar la columna Imagen a la tabla Productos
-- Ejecutar en SQL Server Management Studio o Azure Data Studio

-- Agregar columna Imagen si no existe
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID('sc_ventas.Productos') 
    AND name = 'Imagen'
)
BEGIN
    ALTER TABLE sc_ventas.Productos
    ADD Imagen NVARCHAR(255) NULL;
    
    PRINT 'Columna Imagen agregada exitosamente a la tabla Productos';
END
ELSE
BEGIN
    PRINT 'La columna Imagen ya existe en la tabla Productos';
END

