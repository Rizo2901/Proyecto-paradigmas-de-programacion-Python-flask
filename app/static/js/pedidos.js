// Variables globales
let pedidos = [];
let clientes = [];
let productos = [];
let detallesPedido = [];
let pedidoEditandoId = null;
let detallesOriginales = []; // Para comparar al editar

// Inicialización cuando se carga la página
document.addEventListener("DOMContentLoaded", () => {
    cargarPedidos();
    cargarClientes();
    cargarProductos();
});

(() => {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
  
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        // Activa estilos de error
        form.classList.add('was-validated');
      }, false);
    });
  })();
  

// Función para cargar pedidos
async function cargarPedidos() {
    try {
        const filtroEstado = document.getElementById("filtroEstado");
        const estado = filtroEstado ? filtroEstado.value : "";
        const url = estado && estado !== "" ? `/pedidos?estado=${estado}` : "/pedidos";
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        pedidos = data;
        renderizarPedidos();
    } catch (error) {
        console.error("Error al cargar pedidos:", error);
        mostrarError("Error al cargar los pedidos: " + error.message);
    }
}

// Función para cargar clientes
async function cargarClientes() {
    try {
        const response = await fetch("/clientes");
        const data = await response.json();
        clientes = data;
        
        const select = document.getElementById("idCliente");
        select.innerHTML = '<option value="">Seleccione un cliente</option>';
        data.forEach(cliente => {
            const option = document.createElement("option");
            option.value = cliente.IdCliente;
            option.textContent = `${cliente.Nombre} (${cliente.Correo})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Error al cargar clientes:", error);
    }
}

// Función para cargar productos
async function cargarProductos() {
    try {
        const response = await fetch("/productos");
        const data = await response.json();
        productos = data.filter(p => p.Activo && p.Stock > 0);
    } catch (error) {
        console.error("Error al cargar productos:", error);
    }
}

// Función para renderizar pedidos en la tabla
function renderizarPedidos() {
    const tbody = document.getElementById("pedidos-tbody");
    
    if (pedidos.length === 0) {
        tbody.innerHTML = "<tr><td colspan='7' class='loading'>No hay pedidos registrados</td></tr>";
        return;
    }
    
    tbody.innerHTML = pedidos.map(pedido => {
        const fecha = new Date(pedido.FechaPedido).toLocaleDateString("es-ES");
        const total = pedido.Total.toFixed(2);
        const itemsCount = pedido.Detalles ? pedido.Detalles.length : 0;
        const nombreCliente = pedido.NombreCliente || `Cliente #${pedido.IdCliente}`;
        
        return `
            <tr>
                <td>${pedido.IdPedido}</td>
                <td>${nombreCliente}</td>
                <td>${fecha}</td>
                <td>$${total}</td>
                <td><span class="estado-badge estado-${pedido.Estado.toLowerCase().replace(' ', '-')}">${pedido.Estado}</span></td>
                <td>${itemsCount} items</td>
                <td class="acciones">
                    <button class="btn-icon" onclick="verDetalles(${pedido.IdPedido})" title="Ver detalles">👁️</button>
                    ${pedido.Estado === "Pendiente" ? `
                        <button class="btn-icon" onclick="editarPedido(${pedido.IdPedido})" title="Editar">✏️</button>
                        <button class="btn-icon" onclick="cambiarEstado(${pedido.IdPedido})" title="Cambiar estado">🔄</button>
                    ` : ""}
                    <button class="btn-icon btn-danger" onclick="abrirModalEliminar(${pedido.IdPedido})" title="Eliminar">🗑️</button>
                </td>
            </tr>
        `;
    }).join("");
}

// Función para abrir modal de crear pedido
function abrirModalCrear() {
    pedidoEditandoId = null;
    detallesPedido = [];
    detallesOriginales = [];
    document.getElementById("modalTitulo").textContent = "Nuevo Pedido";
    document.getElementById("pedidoId").value = "";
    document.getElementById("idCliente").value = "";
    document.getElementById("idCliente").disabled = false;
    document.getElementById("estado").value = "Pendiente";
    document.getElementById("totalPedido").textContent = "0.00";
    document.getElementById("detalles-list").innerHTML = "";
    document.getElementById("modalPedido").style.display = "block";
}

// Función para editar pedido
async function editarPedido(idPedido) {
    try {
        const response = await fetch(`/pedidos/${idPedido}`);
        const pedido = await response.json();
        
        if (pedido.error) {
            mostrarError(pedido.error);
            return;
        }
        
        // Validar que el pedido esté en estado Pendiente
        if (pedido.Estado !== "Pendiente") {
            mostrarError(`Solo se pueden editar pedidos en estado Pendiente. Estado actual: ${pedido.Estado}`);
            return;
        }
        
        pedidoEditandoId = idPedido;
        detallesPedido = JSON.parse(JSON.stringify(pedido.Detalles || [])); // Copia profunda
        detallesOriginales = JSON.parse(JSON.stringify(pedido.Detalles || [])); // Guardar originales para comparar
        
        document.getElementById("modalTitulo").textContent = `Editar Pedido #${idPedido}`;
        document.getElementById("pedidoId").value = idPedido;
        document.getElementById("idCliente").value = pedido.IdCliente;
        document.getElementById("estado").value = pedido.Estado;
        document.getElementById("idCliente").disabled = true; // No se puede cambiar el cliente
        
        renderizarDetalles();
        calcularTotal();
        
        document.getElementById("modalPedido").style.display = "block";
    } catch (error) {
        console.error("Error al cargar pedido:", error);
        mostrarError("Error al cargar el pedido");
    }
}

// Función para cerrar modal
function cerrarModal() {
    document.getElementById("modalPedido").style.display = "none";
    pedidoEditandoId = null;
    detallesPedido = [];
    detallesOriginales = [];
}

// Función para agregar detalle
function agregarDetalle() {
    detallesPedido.push({
        IdDetalle: null,
        IdProducto: "",
        Cantidad: 1,
        PrecioUnitario: 0,
        NombreProducto: ""
    });
    renderizarDetalles();
}

// Función para renderizar detalles
function renderizarDetalles() {
    const container = document.getElementById("detalles-list");
    container.innerHTML = detallesPedido.map((detalle, index) => {
        const producto = productos.find(p => p.IdProducto == detalle.IdProducto);
        const stockDisponible = producto ? producto.Stock : 0;
        
        return `
            <div class="detalle-item" data-index="${index}">
                <select class="producto-select" onchange="actualizarDetalleProducto(${index}, this.value)">
                    <option value="">Seleccione una carta</option>
                    ${productos.map(p => {
                        const selected = p.IdProducto == detalle.IdProducto ? "selected" : "";
                        const stockWarning = p.Stock === 0 ? " (Sin stock)" : ` (Stock: ${p.Stock})`;
                        return `<option value="${p.IdProducto}" ${selected} ${p.Stock === 0 && !selected ? "disabled" : ""}>${p.Nombre} - $${p.Precio}${stockWarning}</option>`;
                    }).join("")}
                </select>
                <input type="number" class="cantidad-input" min="1" value="${detalle.Cantidad}" 
                       onchange="actualizarDetalleCantidad(${index}, this.value)"
                       max="${stockDisponible}">
                <span class="precio-unitario">$${detalle.PrecioUnitario ? detalle.PrecioUnitario.toFixed(2) : "0.00"}</span>
                <span class="subtotal">$${((detalle.Cantidad || 0) * (detalle.PrecioUnitario || 0)).toFixed(2)}</span>
                <button type="button" class="btn-icon btn-danger" onclick="eliminarDetalle(${index})" title="Eliminar">🗑️</button>
            </div>
        `;
    }).join("");
    calcularTotal();
}

// Función para actualizar producto en detalle
function actualizarDetalleProducto(index, idProducto) {
    const producto = productos.find(p => p.IdProducto == idProducto);
    if (producto) {
        detallesPedido[index].IdProducto = producto.IdProducto;
        detallesPedido[index].NombreProducto = producto.Nombre;
        detallesPedido[index].PrecioUnitario = producto.Precio;
        detallesPedido[index].Cantidad = Math.min(detallesPedido[index].Cantidad || 1, producto.Stock);
        renderizarDetalles();
    }
}

// Función para actualizar cantidad en detalle
function actualizarDetalleCantidad(index, cantidad) {
    const cantidadNum = parseInt(cantidad) || 1;
    const detalle = detallesPedido[index];
    const producto = productos.find(p => p.IdProducto == detalle.IdProducto);
    
    if (producto && cantidadNum > producto.Stock) {
        mostrarError(`Stock insuficiente. Disponible: ${producto.Stock}`);
        detallesPedido[index].Cantidad = producto.Stock;
    } else {
        detallesPedido[index].Cantidad = cantidadNum;
    }
    renderizarDetalles();
}

// Función para eliminar detalle
function eliminarDetalle(index) {
    detallesPedido.splice(index, 1);
    renderizarDetalles();
}

// Función para calcular total
function calcularTotal() {
    const total = detallesPedido.reduce((sum, detalle) => {
        return sum + ((detalle.Cantidad || 0) * (detalle.PrecioUnitario || 0));
    }, 0);
    document.getElementById("totalPedido").textContent = total.toFixed(2);
}

// Función para actualizar un pedido completo (información básica + detalles)
async function actualizarPedidoCompleto(idPedido, formData) {
    try {
        // 1. Actualizar información básica del pedido (Estado)
        const updateResponse = await fetch(`/pedidos/${idPedido}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                Estado: formData.Estado
            })
        });
        
        const updateResult = await updateResponse.json();
        if (updateResult.error) {
            return updateResult;
        }
        
        // 2. Obtener detalles actuales del servidor
        const detallesResponse = await fetch(`/pedidos/${idPedido}/detalles`);
        const detallesActuales = await detallesResponse.json();
        
        if (detallesActuales.error) {
            return detallesActuales;
        }
        
        // 3. Sincronizar detalles: comparar nuevos con actuales
        const detallesNuevos = formData.detalles || [];
        const detallesParaEliminar = [];
        const detallesParaCrear = [];
        const detallesParaActualizar = [];
        
        // Identificar detalles a eliminar (están en actuales pero no en nuevos)
        detallesActuales.forEach(detalleActual => {
            const existeEnNuevos = detallesNuevos.some(d => {
                // Buscar por IdDetalle si existe
                if (detalleActual.IdDetalle) {
                    return d.IdDetalle === detalleActual.IdDetalle;
                }
                return false;
            });
            
            if (!existeEnNuevos) {
                detallesParaEliminar.push(detalleActual);
            }
        });
        
        // Identificar detalles a crear/actualizar
        detallesNuevos.forEach(detalleNuevo => {
            // Buscar detalle existente por IdDetalle si está disponible
            let detalleExistente = null;
            if (detalleNuevo.IdDetalle) {
                detalleExistente = detallesActuales.find(d => d.IdDetalle === detalleNuevo.IdDetalle);
            }
            
            // Si no se encontró por IdDetalle, buscar por IdProducto
            if (!detalleExistente) {
                detalleExistente = detallesActuales.find(d => d.IdProducto === detalleNuevo.IdProducto);
            }
            
            if (!detalleExistente) {
                // Nuevo detalle a crear
                detallesParaCrear.push({
                    IdProducto: detalleNuevo.IdProducto,
                    Cantidad: detalleNuevo.Cantidad,
                    PrecioUnitario: detalleNuevo.PrecioUnitario
                });
            } else {
                // Verificar si necesita actualización
                const cambioCantidad = detalleExistente.Cantidad !== detalleNuevo.Cantidad;
                const cambioPrecio = Math.abs((detalleExistente.PrecioUnitario || 0) - (detalleNuevo.PrecioUnitario || 0)) > 0.01;
                const cambioProducto = detalleExistente.IdProducto !== detalleNuevo.IdProducto;
                
                if (cambioCantidad || cambioPrecio || cambioProducto) {
                    if (cambioProducto) {
                        // Si cambió el producto, eliminar el viejo y crear uno nuevo
                        detallesParaEliminar.push(detalleExistente);
                        detallesParaCrear.push({
                            IdProducto: detalleNuevo.IdProducto,
                            Cantidad: detalleNuevo.Cantidad,
                            PrecioUnitario: detalleNuevo.PrecioUnitario
                        });
                    } else {
                        // Actualizar detalle existente
                        detallesParaActualizar.push({
                            idDetalle: detalleExistente.IdDetalle,
                            data: {
                                Cantidad: detalleNuevo.Cantidad,
                                PrecioUnitario: detalleNuevo.PrecioUnitario
                            }
                        });
                    }
                }
            }
        });
        
        // 4. Ejecutar cambios: primero eliminar, luego crear, luego actualizar
        // Eliminar detalles
        for (const detalle of detallesParaEliminar) {
            const deleteResponse = await fetch(`/pedidos/${idPedido}/detalles/${detalle.IdDetalle}`, {
                method: "DELETE"
            });
            const deleteResult = await deleteResponse.json();
            if (deleteResult.error) {
                return deleteResult;
            }
        }
        
        // Crear nuevos detalles
        for (const detalle of detallesParaCrear) {
            const createResponse = await fetch(`/pedidos/${idPedido}/detalles`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(detalle)
            });
            const createResult = await createResponse.json();
            if (createResult.error) {
                return createResult;
            }
        }
        
        // Actualizar detalles existentes
        for (const { idDetalle, data } of detallesParaActualizar) {
            const updateResponse = await fetch(`/pedidos/${idPedido}/detalles/${idDetalle}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            const updateResult = await updateResponse.json();
            if (updateResult.error) {
                return updateResult;
            }
        }
        
        // 5. Obtener el pedido actualizado
        const finalResponse = await fetch(`/pedidos/${idPedido}`);
        return await finalResponse.json();
        
    } catch (error) {
        console.error("Error al actualizar pedido:", error);
        return { error: `Error al actualizar pedido: ${error.message}` };
    }
}

// Función para guardar pedido
document.getElementById("formPedido").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    if (detallesPedido.length === 0) {
        mostrarError("El pedido debe tener al menos un detalle");
        return;
    }
    
    // Validar stock antes de enviar
    for (const detalle of detallesPedido) {
        const producto = productos.find(p => p.IdProducto == detalle.IdProducto);
        if (!producto) {
            mostrarError(`Producto no encontrado: ${detalle.NombreProducto}`);
            return;
        }
        if (producto.Stock < detalle.Cantidad) {
            mostrarError(`Stock insuficiente para ${producto.Nombre}. Disponible: ${producto.Stock}, solicitado: ${detalle.Cantidad}`);
            return;
        }
    }
    
    const formData = {
        IdCliente: parseInt(document.getElementById("idCliente").value),
        Estado: document.getElementById("estado").value,
        detalles: detallesPedido.map(d => ({
            IdDetalle: d.IdDetalle || null, // Preservar IdDetalle si existe
            IdProducto: parseInt(d.IdProducto),
            Cantidad: parseInt(d.Cantidad),
            PrecioUnitario: parseFloat(d.PrecioUnitario)
        }))
    };
    
    try {
        let resultado;
        if (pedidoEditandoId) {
            // Actualizar pedido existente
            resultado = await actualizarPedidoCompleto(pedidoEditandoId, formData);
        } else {
            // Crear nuevo pedido
            const response = await fetch("/pedidos", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });
            resultado = await response.json();
        }
        
        if (resultado.error) {
            mostrarError(resultado.error);
        } else {
            cerrarModal();
            cargarPedidos();
            mostrarExito(pedidoEditandoId ? "Pedido actualizado correctamente" : "Pedido guardado correctamente");
        }
    } catch (error) {
        console.error("Error al guardar pedido:", error);
        mostrarError("Error al guardar el pedido: " + error.message);
    }
});

// Función para ver detalles del pedido
async function verDetalles(idPedido) {
    try {
        const response = await fetch(`/pedidos/${idPedido}`);
        const pedido = await response.json();
        
        if (pedido.error) {
            mostrarError(pedido.error);
            return;
        }
        
        document.getElementById("detallesPedidoId").textContent = idPedido;
        const contenido = document.getElementById("detalles-contenido");
        
        const nombreClienteDetalle = pedido.NombreCliente || `Cliente #${pedido.IdCliente}`;
        contenido.innerHTML = `
            <div class="detalles-info">
                <p><strong>Cliente:</strong> ${nombreClienteDetalle}</p>
                <p><strong>Fecha:</strong> ${new Date(pedido.FechaPedido).toLocaleString("es-ES")}</p>
                <p><strong>Estado:</strong> ${pedido.Estado}</p>
                <p><strong>Total:</strong> $${pedido.Total.toFixed(2)}</p>
            </div>
            <table class="detalles-table">
                <thead>
                    <tr>
                        <th>Carta</th>
                        <th>Cantidad</th>
                        <th>Precio Unitario</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    ${(pedido.Detalles || []).map(d => `
                        <tr>
                            <td>${d.NombreProducto}</td>
                            <td>${d.Cantidad}</td>
                            <td>$${d.PrecioUnitario.toFixed(2)}</td>
                            <td>$${d.Subtotal.toFixed(2)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
        
        document.getElementById("modalDetalles").style.display = "block";
    } catch (error) {
        console.error("Error al cargar detalles:", error);
        mostrarError("Error al cargar los detalles del pedido");
    }
}

// Función para cerrar modal de detalles
function cerrarModalDetalles() {
    document.getElementById("modalDetalles").style.display = "none";
}

// Función para cambiar estado del pedido
async function cambiarEstado(idPedido) {
    // Estados válidos según el CHECK constraint de la base de datos
    const estados = ["Pendiente", "Enviado", "Entregado", "Pagado", "Cancelado"];
    const pedido = pedidos.find(p => p.IdPedido === idPedido);
    if (!pedido) return;
    
    const estadoActual = pedido.Estado;
    const indiceActual = estados.indexOf(estadoActual);
    const nuevoEstado = estados[(indiceActual + 1) % estados.length];
    
    try {
        const response = await fetch(`/pedidos/${idPedido}/estado`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estado: nuevoEstado })
        });
        
        const resultado = await response.json();
        
        if (resultado.error) {
            mostrarError(resultado.error);
        } else {
            cargarPedidos();
            mostrarExito(`Estado cambiado a ${nuevoEstado}`);
        }
    } catch (error) {
        console.error("Error al cambiar estado:", error);
        mostrarError("Error al cambiar el estado del pedido");
    }
}

// Función para abrir modal de eliminar
let pedidoEliminarId = null;
function abrirModalEliminar(idPedido) {
    pedidoEliminarId = idPedido;
    document.getElementById("pedidoIdEliminar").textContent = idPedido;
    document.getElementById("modalEliminar").style.display = "block";
}

// Función para cerrar modal de eliminar
function cerrarModalEliminar() {
    document.getElementById("modalEliminar").style.display = "none";
    pedidoEliminarId = null;
}

// Función para confirmar eliminación
async function confirmarEliminar() {
    if (!pedidoEliminarId) return;
    
    try {
        const response = await fetch(`/pedidos/${pedidoEliminarId}`, {
            method: "DELETE"
        });
        
        const resultado = await response.json();
        
        if (resultado.error) {
            mostrarError(resultado.error);
        } else {
            cerrarModalEliminar();
            cargarPedidos();
            mostrarExito("Pedido eliminado correctamente");
        }
    } catch (error) {
        console.error("Error al eliminar pedido:", error);
        mostrarError("Error al eliminar el pedido");
    }
}

// Funciones de utilidad
function mostrarError(mensaje) {
    alert("Error: " + mensaje);
}

function mostrarExito(mensaje) {
    alert("Éxito: " + mensaje);
}

// Cerrar modales al hacer click fuera
window.onclick = function(event) {
    const modalPedido = document.getElementById("modalPedido");
    const modalDetalles = document.getElementById("modalDetalles");
    const modalEliminar = document.getElementById("modalEliminar");
    
    if (event.target === modalPedido) {
        cerrarModal();
    }
    if (event.target === modalDetalles) {
        cerrarModalDetalles();
    }
    if (event.target === modalEliminar) {
        cerrarModalEliminar();
    }
}

