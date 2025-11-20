# 🃏 ProyectoCartasPokemon
Aplicación web desarrollada con **Flask + SQLAlchemy + SQL Server** diseñada para gestionar un sistema de tienda en línea basado en cartas Pokémon.  
Incluye manejo de clientes, productos, pedidos, carritos y servicios organizados en una arquitectura modular.

---

## 📁 **Estructura del Proyecto**
ProyectoCartasPokemon/
│── .venv/
│── app/
│ ├── init.py
│ ├── extensions.py
│ ├── models/
│ │ ├── carrito.py
│ │ ├── carrito_detalle.py
│ │ ├── clientes.py
│ │ ├── pedidos.py
│ │ ├── productos.py
│ ├── routes/
│ ├── services/
│ ├── utils/
│── config/
│ ├── base.py
│ ├── db.py
│ ├── dev.py
│ ├── prod.py
│ ├── init.py
│── migrations/
│── run.py
│── requirements.txt
│── .env

---

# 🧩 **Descripción de Carpetas y su Función**

A continuación se detalla **qué hace cada carpeta**, qué clases contiene y su intención dentro de la arquitectura.

---

## 📂 **/app**
Contiene toda la lógica principal de la aplicación Flask.

### ✔️ `__init__.py`
Responsable de:
- Crear la aplicación Flask (`create_app`)
- Cargar configuraciones (`dev`, `prod`)
- Inicializar extensiones (SQLAlchemy)
- Registrar blueprints de rutas

---

## ⚙️ **/app/extensions.py**
Centraliza las extensiones usadas por la app.

### Contiene:
- `db = SQLAlchemy()`

**Intención:**  
Evitar ciclos de importación y permitir que SQLAlchemy sea reutilizable en toda la app.

---

## 🗂️ **/app/models/**
Modelos de base de datos representados como clases de SQLAlchemy.

Cada archivo contiene un modelo de tabla:

### 📌 `clientes.py`
Representa a los clientes del sistema.
Incluye:
- id
- nombre
- email
- dirección
- fecha de registro

### 📌 `productos.py`
Representa los productos (cartas Pokémon).
Incluye:
- id
- nombre
- descripción
- precio
- stock
- imagen

### 📌 `carrito.py`
Representa el carrito de compras de un cliente.
Incluye:
- id
- id_cliente
- total
- fecha creación

### 📌 `carrito_detalle.py`
Representa los ítems dentro del carrito.
Incluye:
- id
- id_carrito
- id_producto
- cantidad
- subtotal


### 📌 `pedidos.py`
Representa los pedidos realizados por los usuarios.
Incluye:
- id
- id_cliente
- monto total
- estado del pedido
- fecha creación

**Intención general de /models:**  
Crear toda la capa ORM del proyecto para que la base de datos se maneje como objetos.

---

## 🌐 **/app/routes/**
Contiene los blueprints de endpoints.

### Cada archivo define rutas relacionadas a un módulo:
- `main.py` — rutas generales
- `productos.py` — CRUD de productos
- `clientes.py` — manejo de clientes
- `carrito.py` — lógica del carrito

**Intención:**  
Encapsular rutas por módulo y mantener el código limpio y escalable.

---

## 🛠️ **/app/services/**
Contiene lógica de negocio (servicios).

### Ejemplos típicos:
- Procesar un pedido
- Calcular totales del carrito
- Validar stock
- Autenticación
- Envío de correos

**Intención:**  
Separar reglas de negocio de rutas y modelos.

---

## 🔧 **/app/utils/**
Herramientas/helper functions reutilizables.

### Ejemplos:
- Validaciones
- Conversión de formatos
- Funciones matemáticas o auxiliares

**Intención:**  
Evitar código duplicado y centralizar utilidades.

---

# ⚙️ **Configuraciones (Carpeta /config)**

## 📌 `base.py`
Clase base que define la configuración general.

Incluye:
- SECRET_KEY
- SQLALCHEMY_DATABASE_URI (construida desde variables `.env`)
- Variables de entorno comunes

### Clase principal:
- `BaseConfig`

---

## 📌 `dev.py`
Configuración para desarrollo.

### Clase:
- `DevConfig(BaseConfig)`
- Activa `DEBUG = True`

---

## 📌 `prod.py`
Configuración para producción.

### Clase:
- `ProdConfig(BaseConfig)`
- `DEBUG = False`

---

## 📌 `db.py`
Puede contener herramientas adicionales para la base de datos:

- Funciones de inicialización
- Conexiones personalizadas
- Scripts de migración

---

## 📌 `__init__.py`
Expone un diccionario `config_dict`:

```python
config_dict = {
    "dev": DevConfig,
    "prod": ProdConfig
}
🗄️ /migrations
Generado por Flask-Migrate.

Aquí se guardan:

Cambios en el esquema de BD

Versiones del modelo ORM

🚀 /run.py
Punto principal para levantar la aplicación:

python
Copiar código
from app import create_app
app = create_app("dev")
app.run()
📦 requirements.txt
Lista las dependencias necesarias del proyecto.

Incluye:

Flask

Flask SQLAlchemy

PyODBC

python-dotenv

Flask-Migrate
… etc.

🔐 .env
Contiene variables sensibles:

ini
Copiar código
DB_SERVER=localhost
DB_NAME=DB_TiendaOnline
DB_USER=db_connect
DB_PASSWORD=2901*
DB_DRIVER=ODBC+Driver+17+for+SQL+Server

FLASK_ENV=development
SECRET_KEY=tu_clave_secreta
▶️ Cómo levantar el proyecto
bash
Copiar código
# Activar entorno virtual
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el servidor
python run.py
Abrir en navegador:
👉 http://127.0.0.1:5000/

🤝 Contribuciones
Pull requests son bienvenidos.
Para cambios mayores, por favor abre un issue primero.

📄 Licencia
Este proyecto está bajo la licencia MIT.


