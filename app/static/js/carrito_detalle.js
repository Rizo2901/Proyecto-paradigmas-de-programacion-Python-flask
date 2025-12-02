// ================= Variables globales =================
let carritoItems = 0;
let idCarrito = 0; // se llenará desde el DOM

// ================= Validación Bootstrap =================
(() => {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();

// ================= Inicialización =================
document.addEventListener("DOMContentLoaded", () => {
    // leer idCarrito desde el input hidden (si existe)
    idCarrito = Number(document.getElementById("idCarrito")?.value || 0);
    // Vincular evento submit del formulario de agregar con JS
    const formAgregar = document.getElementById("formAgregar");
    if (formAgregar) {
        formAgregar.addEventListener("submit", handleAgregarForm);
    }
    // Vincular evento submit del formulario de editar
    const formEditar = document.getElementById("formEditar");
    if (formEditar) {
        formEditar.addEventListener("submit", handleEditarForm);
    }
    // Vincular evento submit del formulario eliminar
    const formEliminar = document.getElementById("formEliminar");
    if (formEliminar) {
        formEliminar.addEventListener("submit", handleEliminarForm);
    }
    actualizarContadorCarrito();
});

// ================= CRUD CarritoDetalle =================

// Actualizar contador del carrito
async function actualizarContadorCarrito() {
    try {
        const response = await fetch(`/carrito_detalle/total`);
        if (response.ok) {
            const data = await response.json();
            carritoItems = data.CantidadTotal || data.Items || 0;
            const badge = document.getElementById("cartBadge");
            if (badge) {
                badge.textContent = carritoItems;
                badge.style.display = carritoItems === 0 ? "none" : "flex";
            }
        } else {
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
document.addEventListener("DOMContentLoaded", () => {
    const hidden = document.getElementById("idCarrito");
    if (hidden) {
        idCarrito = parseInt(hidden.value) || 0;
    }

    document.querySelectorAll(".btn-add-cart").forEach(btn => {
        btn.addEventListener("click", () => {
            const idProducto = btn.getAttribute("data-product-id");
            agregarAlCarrito(idProducto, 1);
        });
    });
});

// Crear: agregar producto al carrito
// Crear: agregar producto al carrito
async function agregarAlCarrito(idProducto, cantidad = 1) {
    if (!idProducto || cantidad <= 0) {
        mostrarMensajeCarrito("Debe seleccionar un producto y cantidad válida", "error");
        return;
    }

    try {
        const response = await fetch(`/carrito_detalle/items/${idCarrito}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ IdProducto: idProducto, Cantidad: cantidad })
        });

        const resultado = await response.json().catch(() => ({}));
        console.log("agregarAlCarrito response", response.status, resultado);

        if (response.ok && !resultado.error) {
            // 🚀 Actualizar idCarrito si el backend devolvió uno nuevo
            if (resultado.IdCarrito && resultado.IdCarrito !== idCarrito) {
                idCarrito = resultado.IdCarrito;
                const hidden = document.getElementById("idCarrito");
                if (hidden) hidden.value = idCarrito;
                console.log("Nuevo IdCarrito asignado:", idCarrito);
            }

            await actualizarContadorCarrito();
            mostrarMensajeCarrito("✓ Producto agregado al carrito", "success");

            // ✅ Recargar la página completa como cualquier sitio normal
            location.reload();

        } else {
            mostrarMensajeCarrito(resultado.error || "Error al agregar al carrito", "error");
        }
    } catch (error) {
        console.error("Error al agregar al carrito:", error);
        mostrarMensajeCarrito("Error al agregar al carrito", "error");
    }
}



// Editar: actualizar cantidad de un producto
async function editarCantidadCarrito(idDetalle, nuevaCantidad, nuevoProductoId) {
    if (nuevaCantidad <= 0) {
        mostrarMensajeCarrito("La cantidad debe ser mayor que 0", "error");
        return;
    }

    try {
        const payload = { Cantidad: nuevaCantidad };
        if (nuevoProductoId && Number(nuevoProductoId) > 0) payload.IdProducto = Number(nuevoProductoId);

        const response = await fetch(`/carrito_detalle/items/${idDetalle}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const resultado = await response.json().catch(() => ({}));
        console.log("editarCantidadCarrito response", response.status, resultado);

        if (response.ok && !resultado.error) {
            await actualizarContadorCarrito();
            // Si el IdDetalle retornado difiere del enviado, el detalle fue fusionado a otro Id
            if (resultado && resultado.IdDetalle && Number(resultado.IdDetalle) !== Number(idDetalle)) {
                mostrarMensajeCarrito("✓ Producto cambiado y fusionado en el carrito", "success");
            } else {
                mostrarMensajeCarrito("✓ Cantidad actualizada", "success");
            }
            location.reload();
        } else {
            mostrarMensajeCarrito(resultado.error || "Error al actualizar cantidad", "error");
        }
    } catch (error) {
        console.error("Error al editar cantidad:", error);
        mostrarMensajeCarrito("Error al editar cantidad", "error");
    }
}

// Eliminar: quitar producto del carrito
async function eliminarDelCarrito(idDetalle) {
    try {
        const response = await fetch(`/carrito_detalle/items/${idDetalle}`, {
            method: "DELETE"
        });

        const resultado = await response.json().catch(() => ({}));
        console.log("eliminarDelCarrito response", response.status, resultado);

        if (response.ok && !resultado.error) {
            await actualizarContadorCarrito();
            mostrarMensajeCarrito("✓ Producto eliminado del carrito", "success");
            location.reload();
        } else {
            mostrarMensajeCarrito(resultado.error || "Error al eliminar producto", "error");
        }
    } catch (error) {
        console.error("Error al eliminar producto:", error);
        mostrarMensajeCarrito("Error al eliminar producto", "error");
    }
}

// Limpiar carrito completo
async function limpiarCarrito() {
    try {
        const response = await fetch(`/carrito_detalle/limpiar`, {
            method: "DELETE"
        });

        const resultado = await response.json().catch(() => ({}));
        console.log("limpiarCarrito response", response.status, resultado);

        if (response.ok && !resultado.error) {
            await actualizarContadorCarrito();
            mostrarMensajeCarrito("✓ Carrito vaciado", "success");
            location.reload();
        } else {
            mostrarMensajeCarrito(resultado.error || "Error al limpiar carrito", "error");
        }
    } catch (error) {
        console.error("Error al limpiar carrito:", error);
        mostrarMensajeCarrito("Error al limpiar carrito", "error");
    }
}

// ================= Utilidades =================

function verCarrito() {
    if (carritoItems === 0) {
        alert("Tu carrito está vacío");
    } else {
        const mensaje = carritoItems === 1
            ? `Tienes ${carritoItems} producto en tu carrito`
            : `Tienes ${carritoItems} productos en tu carrito`;
        alert(mensaje);
        // Ejemplo: window.location.href = `/carrito_detalle/pagina`;
    }
}

function mostrarMensajeCarrito(mensaje, tipo) {
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

    mensajeElement.style.background = tipo === "success"
        ? "linear-gradient(135deg, #48bb78 0%, #38a169 100%)"
        : "linear-gradient(135deg, #f56565 0%, #e53e3e 100%)";

    mensajeElement.textContent = mensaje;
    mensajeElement.style.display = "block";

    setTimeout(() => {
        mensajeElement.style.animation = "slideOutRight 0.3s ease-out";
        setTimeout(() => { mensajeElement.style.display = "none"; }, 300);
    }, 3000);
}

// manejadores de formularios
async function handleAgregarForm(e){
    e.preventDefault();
    const idProducto = Number(document.getElementById("producto").value || 0);
    const cantidad = Number(document.getElementById("cantidad").value || 1);
    if (!idProducto) return mostrarMensajeCarrito("Selecciona un producto", "error");

    if (!idCarrito || idCarrito === 0){
        try{
            const response = await fetch(`/carrito/1/agregar/${idProducto}`, { method: "POST" });
            const resultado = await response.json().catch(()=> ({}));
            if (response.ok && !resultado.error){
                mostrarMensajeCarrito("✓ Producto agregado al carrito", "success");

                // ✅ Actualizar contador
                await actualizarContadorCarrito();

                // ✅ Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById("agregarModal"));
                if (modal) modal.hide();

                // ✅ Opcional: actualizar tabla del carrito dinámicamente
                // agregarFilaCarrito(resultado);
            } else {
                mostrarMensajeCarrito(resultado.error || "Error al agregar al carrito", "error");
            }
        } catch (err){
            console.error(err);
            mostrarMensajeCarrito("Error al agregar al carrito", "error");
        }
    } else {
        await agregarAlCarrito(idProducto, cantidad);
        const modal = bootstrap.Modal.getInstance(document.getElementById("agregarModal"));
        if (modal) modal.hide();
    }
}

async function handleEditarForm(e){
    e.preventDefault();
    const idDetalle = Number(document.getElementById("editarDetalleId").value || 0);
    const nuevaCantidad = Number(document.getElementById("editarCantidad").value || 1);
    const nuevoProductoId = Number(document.getElementById("editarProductoId").value || 0);
    console.log("handleEditarForm: idDetalle, nuevaCantidad", idDetalle, nuevaCantidad);
    if (!idDetalle) return mostrarMensajeCarrito("Detalle inválido", "error");
    await editarCantidadCarrito(idDetalle, nuevaCantidad, nuevoProductoId);
}

async function handleEliminarForm(e){
    e.preventDefault();
    const idDetalle = Number(document.getElementById("eliminarDetalleId").value || 0);
    if (!idDetalle) return mostrarMensajeCarrito("Detalle inválido", "error");
    await eliminarDelCarrito(idDetalle);
}

