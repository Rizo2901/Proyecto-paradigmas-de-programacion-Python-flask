// Variables globales para el carrito
let clienteId = 1; // Por defecto cliente ID 1, esto se puede cambiar después
let carritoItems = 0;

// Inicialización cuando se carga la página
document.addEventListener("DOMContentLoaded", () => {
    actualizarContadorCarrito();
});

// Función para actualizar el contador del carrito
async function actualizarContadorCarrito() {
    try {
        const response = await fetch(`/carrito/${clienteId}/total`);
        if (response.ok) {
            const data = await response.json();
            carritoItems = data.CantidadTotal || data.Items || 0;
            const badge = document.getElementById("cartBadge");
            if (badge) {
                badge.textContent = carritoItems;
                if (carritoItems === 0) {
                    badge.style.display = "none";
                } else {
                    badge.style.display = "flex";
                }
            }
        } else {
            // Si no hay carrito, el contador se queda en 0
            const badge = document.getElementById("cartBadge");
            if (badge) {
                badge.textContent = "0";
                badge.style.display = "none";
            }
        }
    } catch (error) {
        console.error("Error al actualizar contador del carrito:", error);
    }
}

// Función para agregar producto al carrito
async function agregarAlCarrito(idProducto) {
    try {
        const response = await fetch(`/carrito/${clienteId}/items`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                IdProducto: idProducto,
                Cantidad: 1
            })
        });

        const resultado = await response.json();

        if (response.ok && !resultado.error) {
            // Actualizar contador
            await actualizarContadorCarrito();
            
            // Mostrar mensaje de éxito
            mostrarMensajeCarrito("✓ Producto agregado al carrito", "success");
        } else {
            // Mostrar error
            mostrarMensajeCarrito(resultado.error || "Error al agregar al carrito", "error");
        }
    } catch (error) {
        console.error("Error al agregar al carrito:", error);
        mostrarMensajeCarrito("Error al agregar al carrito", "error");
    }
}

// Función para ver el carrito (se puede implementar después)
function verCarrito() {
    // Por ahora solo muestra un mensaje, pero se puede crear una página de carrito
    if (carritoItems === 0) {
        alert("Tu carrito está vacío");
    } else {
        const mensaje = carritoItems === 1 
            ? `Tienes ${carritoItems} producto en tu carrito`
            : `Tienes ${carritoItems} productos en tu carrito`;
        alert(mensaje);
        // Aquí se puede redirigir a una página de carrito o abrir un modal
        // window.location.href = `/carrito/${clienteId}`;
    }
}

// Función para mostrar mensajes temporales
function mostrarMensajeCarrito(mensaje, tipo) {
    // Crear elemento de mensaje si no existe
    let mensajeElement = document.getElementById("carrito-mensaje");
    if (!mensajeElement) {
        mensajeElement = document.createElement("div");
        mensajeElement.id = "carrito-mensaje";
        mensajeElement.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 3000;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        `;
        document.body.appendChild(mensajeElement);
    }

    // Establecer color según el tipo
    if (tipo === "success") {
        mensajeElement.style.background = "linear-gradient(135deg, #48bb78 0%, #38a169 100%)";
    } else {
        mensajeElement.style.background = "linear-gradient(135deg, #f56565 0%, #e53e3e 100%)";
    }

    mensajeElement.textContent = mensaje;
    mensajeElement.style.display = "block";

    // Ocultar después de 3 segundos
    setTimeout(() => {
        mensajeElement.style.animation = "slideOutRight 0.3s ease-out";
        setTimeout(() => {
            mensajeElement.style.display = "none";
        }, 300);
    }, 3000);
}

// Función para establecer el cliente (útil si hay sistema de login)
function establecerCliente(id) {
    clienteId = id;
    actualizarContadorCarrito();
}

// Agregar animación CSS si no existe
if (!document.getElementById("carrito-animations")) {
    const style = document.createElement("style");
    style.id = "carrito-animations";
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

