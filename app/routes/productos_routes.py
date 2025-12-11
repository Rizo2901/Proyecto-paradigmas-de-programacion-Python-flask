import os
import uuid
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
from app.services.productos_service import ProductosService

productos_bp = Blueprint("productos", __name__)

# Extensiones permitidas para imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_imagen(file):
    """Guarda la imagen y retorna el nombre del archivo"""
    if file and allowed_file(file.filename):
        # Generar nombre único para evitar colisiones
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Crear directorio si no existe
        upload_folder = os.path.join(current_app.root_path, 'static', 'img', 'cartas')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Guardar archivo
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None

@productos_bp.get("/cartas/pagina")
def pagina_clientes():
    """Página HTML para gestionar cartas"""
    return render_template("cartas/cartas.html")

@productos_bp.get("/productos")
def obtener_productos():
    return jsonify(ProductosService.obtener_todos())

@productos_bp.get("/productos/<int:id_producto>")
def obtener_producto(id_producto):
    return jsonify(ProductosService.obtener_por_id(id_producto))

@productos_bp.post("/productos")
def crear_producto():
    # Obtener datos del formulario (FormData)
    data = {
        "Nombre": request.form.get("Nombre"),
        "Descripcion": request.form.get("Descripcion"),
        "Precio": request.form.get("Precio", 0),
        "Stock": request.form.get("Stock", 0),
        "Activo": request.form.get("Activo", "true").lower() == "true"
    }
    
    # Procesar imagen si existe
    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and file.filename:
            filename = guardar_imagen(file)
            if filename:
                data["Imagen"] = filename
    
    return jsonify(ProductosService.crear(data)), 201

@productos_bp.put("/productos/<int:id_producto>")
def actualizar_producto(id_producto):
    # Obtener datos del formulario (FormData)
    data = {
        "Nombre": request.form.get("Nombre"),
        "Descripcion": request.form.get("Descripcion"),
        "Precio": request.form.get("Precio"),
        "Stock": request.form.get("Stock"),
        "Activo": request.form.get("Activo", "true").lower() == "true"
    }
    
    # Procesar imagen si existe
    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and file.filename:
            filename = guardar_imagen(file)
            if filename:
                data["Imagen"] = filename
    
    return jsonify(ProductosService.actualizar(id_producto, data))

@productos_bp.delete("/productos/<int:id_producto>")
def eliminar_producto(id_producto):
    """Eliminar un producto"""
    resultado = ProductosService.eliminar_fisico(id_producto)
    if "error" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado), 200
